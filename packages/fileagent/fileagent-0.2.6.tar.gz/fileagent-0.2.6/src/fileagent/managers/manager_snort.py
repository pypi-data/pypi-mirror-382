import json
import re


class ManagerSnort:

    def ip_matches(self, data: str) -> str:
        """
        Description:
            Check if the data contains an ip address. Checks for ipv4, ipv6 and url

        Args:
            data (str): Data to be checked for ip address

        Returns:
            str: the ip/url regex matching case
        """
        ipv4_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ipv6_pattern = r"\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b"
        url_pattern = r"\bhttps?://[^\s/$.?#].[^\s]*\b"

        for pattern in [ipv4_pattern, ipv6_pattern, url_pattern]:
            match = re.search(pattern, data)
            if match:
                return match.group(0)
        return None

    def get_ip_from_request(self, request: dict) -> str:
        """
        Description:
            Get the ip address from the request

        Args:
            request (dict): Request data to be checked for ip address

        Returns:
            str: The ip address from the request
        """

        if request.get("content_type") == "application/json":
            data = json.loads(request.get("content"))
            return data.get("ip")
        elif request.get("content_type") == "text/plain":
            return self.ip_matches(request.get("content"))
        else:
            return None

    def rule_translator(self, data: dict) -> str:
        """
        Description:
            Translate the data into a rule
            Right now this is a simple implementation
            Checks if it is a json or text file and extracts the ip address

        Args:
            data (dict): Data from the post request to be translated into a rule,

        Returns:
            str: Rule to be appended to the rules file
        """

        tranlator_book = {
            "block_ip": self.building_rule_block,
            "block_domain": self.building_rule_block_domain,
            "alert_ip": self.building_rule_alert,
            "alert_domain": self.building_rule_alert_domain,
            "block_icmp": self.building_rule_block_icmp,
            "custom": self.building_rule_custom,
        }

        rule = None

        if (command := data.get("command")) in tranlator_book.keys():
            rule = tranlator_book[command](data.get("target"))
        return rule

    def building_rule_block(self, target: str, msg: str = None, verbose=False) -> str:
        """
        Builds a Snort rule to block HTTP traffic from a specific target.

        Args:
            target (str): The target IP address or domain.
            msg (str, optional): Custom message for the rule. Defaults to None.
            verbose (bool, optional): If True, prints the rule. Defaults to False.

        Returns:
            str: The formatted Snort rule string.
        """
        parts, opts = self.builder(
            action="block",
            protocol="ip",
            src_ip=target,
            src_port="any",
            direction="->",
            dst_ip="any",
            dst_port="any",
            sid=self.get_current_sid(),
            msg=msg or f"Block traffic From IP {target}",
        )

        rule = self.build_formatter(parts, opts, pretty=True)
        if verbose:
            print(rule)
        return rule

    def building_rule_block_icmp(
        self, target: str, msg: str = None, verbose=False
    ) -> str:
        """
        Builds a Snort rule to block ICMP traffic from a specific target.

        Args:
            target (str): The target IP address.
            msg (str, optional): Custom message for the rule. Defaults to None.
            verbose (bool, optional): If True, prints the rule. Defaults to False.

        Returns:
            str: The formatted Snort rule string.
        """
        parts, opts = self.builder(
            action="block",
            protocol="icmp",
            src_ip=target,
            src_port="any",
            direction="->",
            dst_ip="any",
            dst_port="any",
            sid=self.get_current_sid(),
            msg=msg or f"Block ICMP From IP {target}",
        )

        rule = self.build_formatter(parts, opts, pretty=True)
        if verbose:
            print(rule)
        return rule

    def building_rule_custom(self, rule: str, verbose=False) -> str:
        """
        Returns the custom Snort rule provided from the user.

        Returns:
            str: The formatted Snort rule string.
        """

        return rule

    def building_rule_alert_icmp(
        self, target: str, msg: str = None, verbose=False
    ) -> str:
        """
        Builds a Snort rule to alert on ICMP traffic from a specific target.

        Args:
            target (str): The target IP address.
            msg (str, optional): Custom message for the rule. Defaults to None.
            verbose (bool, optional): If True, prints the rule. Defaults to False.

        Returns:
            str: The formatted Snort rule string.
        """
        parts, opts = self.builder(
            action="alert",
            protocol="icmp",
            src_ip=target,
            src_port="any",
            direction="->",
            dst_ip="any",
            dst_port="any",
            sid=self.get_current_sid(),
            msg=msg or f"Alert ICMP From IP {target}",
        )

        rule = self.build_formatter(parts, opts, pretty=True)

        if verbose:
            print(rule)
        return rule

    def building_rule_block_domain(
        self, domain: str, msg: str = None, verbose=False
    ) -> str:
        """
        Builds a Snort rule to block traffic to a specific domain.

        Args:
            domain (str): The target domain to block.
            msg (str, optional): Custom message for the rule. Defaults to None.
            verbose (bool, optional): If True, prints the rule. Defaults to False.

        Returns:
            str: The formatted Snort rule string.
        """

        parts, opts = self.builder(
            action="block",
            protocol="ssl",
            src_ip="any",
            src_port="any",
            direction="->",
            dst_ip="any",
            dst_port=443,
            sid=self.get_current_sid(),
            ssl_state="client_hello",
            msg=msg or f"Block domain with SNI {domain}",
            content=[{"value": f"|{self.to_hex(domain)}|"}],
        )

        rule = self.build_formatter(parts, opts, pretty=True)

        if verbose:
            print(rule)
        return rule

    def building_rule_alert_domain(
        self, domain: str, msg: str = None, verbose=False
    ) -> str:
        """
        Builds a Snort rule to alert traffic to a specific domain.

        Args:
            domain (str): The target domain to alert.
            msg (str, optional): Custom message for the rule. Defaults to None.
            verbose (bool, optional): If True, prints the rule. Defaults to False.

        Returns:
            str: The formatted Snort rule string.
        """

        parts, opts = self.builder(
            action="alert",
            protocol="ssl",
            src_ip="any",
            src_port="any",
            direction="->",
            dst_ip="any",
            dst_port=443,
            sid=self.get_current_sid(),
            ssl_state="client_hello",
            msg=msg or f"alert domain with SNI {domain}",
            content=[{"value": f"|{self.to_hex(domain)}|"}],
        )

        rule = self.build_formatter(parts, opts, pretty=True)

        if verbose:
            print(rule)
        return rule

    def building_rule_alert(self, target: str, msg: str = None, verbose=False) -> str:
        """
        Builds a Snort rule to alert on IP traffic from a specific target.

        Args:
            target (str): The target IP address.
            msg (str, optional): Custom message for the rule. Defaults to None.
            verbose (bool, optional): If True, prints the rule. Defaults to False.

        Returns:
            str: The formatted Snort rule string.
        """
        parts, opts = self.builder(
            action="alert",
            protocol="ip",
            src_ip=target,
            src_port="any",
            direction="->",
            dst_ip="any",
            dst_port="any",
            msg=msg or f"IP Alert Incoming From IP {target}",
            classtype="tcp-connection",
            sid=self.get_current_sid(),
            rev=1,
        )

        rule = self.build_formatter(parts, opts, pretty=True)
        if verbose:
            print(rule)

        return rule

    def builder(
        self,
        action: str = None,
        rule_type: str = None,
        protocol: str = None,
        src_ip: str = None,
        src_port: int = None,
        direction: str = None,
        dst_ip: str = None,
        dst_port: int = None,
        msg: str = None,
        reference: list[tuple[str, str]] = None,
        gid: int = None,
        sid: int = None,
        rev: int = None,
        classtype: str = None,
        priority: int = None,
        metadata: dict[str, str] = None,
        service_opt: list[str] = None,
        rem: str = None,
        file_meta: dict[str, str] = None,
        content: list[dict[str, str]] = None,
        pcre: list[str] = None,
        regex: list[str] = None,
        bufferlen: int = None,
        isdataat: bool = None,
        dsize: int = None,
        flow: list[str] = None,
        ttl: int = None,
        ipopts: list[str] = None,
        fragoffset: int = None,
        fragbits: str = None,
        priority_bit: str = None,
        dce: str = None,
        ssl_state: str = None,
        verbose: bool = False,
    ) -> list[list[str]]:
        """
        Description:
            Builds a Snort rule string based on the provided parameters.

            This function constructs a Snort rule by combining header fields, general options,
            payload options, and non-payload options. It validates required fields and formats
            the rule according to Snort syntax.

        Args:
            action (str): The action to take (e.g., 'alert', 'drop', 'log', etc.).
            rule_type (str): The type of rule ('traditional', 'service', 'file', 'file_id').
            protocol (str): The protocol to match ('ip', 'icmp', 'tcp', 'udp').
            src_ip (str): The source IP address.
            src_port (int): The source port number.
            direction (str): The direction of traffic ('->', '<>').
            dst_ip (str): The destination IP address.
            dst_port (int): The destination port number.
            msg (str): The message string for the rule.
            reference (list[tuple[str, str]]): List of references as tuples (scheme, id).
            gid (int): Group ID for the rule.
            sid (int): Snort ID for the rule.
            rev (int): Revision number for the rule.
            classtype (str): Classification type for the rule.
            priority (int): Priority level for the rule.
            metadata (dict[str, str]): Metadata key-value pairs.
            service_opt (list[str]): List of service options.
            rem (str): Remarks for the rule.
            file_meta (dict[str, str]): File metadata with keys like type, id, category, etc.
            content (list[dict[str, str]]): Payload content options.
            pcre (list[str]): List of PCRE strings.
            regex (list[str]): List of regex strings.
            bufferlen (int): Buffer length for payload matching.
            isdataat (bool): Indicates if data is at a specific location.
            dsize (int): Data size for payload matching.
            flow (list[str]): List of flow options.
            ttl (int): Time-to-live value.
            ipopts (list[str]): List of IP options.
            fragoffset (int): Fragment offset value.
            fragbits (str): Fragment bits value.
            priority_bit (str): Priority bit value.
            dce (str): DCE/RPC options.
            ssl_state (str): SSL state options.
            pretty (bool): If True, formats the rule for readability.
            verbose (bool): If True, prints the rule to the console.

        Returns:
            list[list[str]]: A list containing the parts and options of the snort rule.
        """

        # build header
        parts = []
        if action in (
            "alert",
            "drop",
            "log",
            "pass",
            "block",
            "react",
            "reject",
            "rewrite",
        ):
            parts.append(action)

        # service/file/file_id rules only need action and keyword
        if rule_type in ("service", "file", "file_id"):
            parts.append(rule_type)
        else:
            # Else it is considered traditional
            for x in (protocol, src_ip, src_port):
                if not x:
                    raise ValueError("protocol, src_ip, src_port required")
                parts.append(x)

            # if direction in ("->", "<>", None):
            #     parts.append(direction or "->")

            parts.append(direction or "->")
            for x in (dst_ip, dst_port):
                if not x:
                    raise ValueError("dst_ip,dst_port required")
                parts.append(x)

        # build options
        opts = []

        def opt(name, val):
            """
            Description:
                Helper function to append options to the opts list.
                If val is a list, it appends each value with the name.
                If val is not None, it appends the name and value.

            Args:
                name (str): The name of the option.
                val (any): The value of the option, can be a list or a single value.
            """
            if isinstance(val, list):
                for v in val:
                    opts.append(f"{name}: {v};")
            elif val is not None:
                opts.append(f"{name}: {val};")

        # general opts
        if msg:
            opts.append(f'msg:"{msg}";')
        if reference:
            # reference is a list of tuples (scheme, id)
            # e.g. [('url', 'example.com'), ('cve', 'CVE-2023-1234')]
            if not isinstance(reference, list):
                raise ValueError("reference must be a list of tuples")
            for scheme, rid in reference:
                opts.append(f"reference:{scheme},{rid};")

        opt("gid", gid)
        opt("sid", sid)
        opt("rev", rev)
        opt("ssl_state", ssl_state)
        if classtype:
            opts.append(f"classtype:{classtype};")

        opt("priority", priority)

        if metadata:
            pairs = [f"{k} {v}" for k, v in metadata.items()]
            opts.append(f"metadata:{','.join(pairs)};")

        if service_opt:
            opts.append(f"service:{','.join(service_opt)};")

        if rem:
            opts.append(f"rem:'{rem}';")

        if file_meta:
            fm = file_meta
            parts = [f"type {fm['type']}", f"id {fm['id']}"]
            for k in ("category", "group", "version"):
                if fm.get(k):
                    parts.append(f"{k} '{fm[k]}'")
            opts.append(f"file_meta:{','.join(parts)};")

        # payload opts example
        if content:
            for c in content:
                segs = [f'content:"{c['value']}"']
                for m in (
                    "fast_pattern",
                    "nocase",
                    "offset",
                    "depth",
                    "distance",
                    "within",
                    "width",
                    "endian",
                ):
                    v = c.get(m)
                    if isinstance(v, bool) and v:
                        segs.append(m)
                    elif v not in (None, False):
                        segs.append(f"{m} {v}")
                opts.append(f"{','.join(segs)};")

        # pcre, regex examples
        if pcre:
            for r in pcre:
                opts.append(f"pcre:'{r}';")

        if regex:
            for r in regex:
                opts.append(f"regex:'{r}';")

        # non-payload example
        if flow:
            opts.append(f"flow:{','.join(flow)};")

        if verbose:
            print("Nothing to verbose. For now ")
        return parts, opts

    def build_formatter(
        self, parts: list[str], opts: list[str], pretty: bool = False
    ) -> str:
        # print(parts)
        header = " ".join(
            list(map(lambda x: x if isinstance(x, str) else str(x), parts))
        )

        # compile rule
        if pretty:
            body = "\n    ".join(opts)
            return f"{header} (\n    {body}\n)"
        else:
            body = " ".join(opts)
            return f"{header} ({body})"

    def to_hex(self, domain: str) -> str:
        """
        Description:
            Convert a domain to hex format for snort rules

        Args:
            domain (str): Domain to be converted

        Returns:
            str: Hex representation of the domain
        """
        return " ".join(f"{ord(c):02x}" for c in domain)

    def append_rule(self, data: dict):
        """
        Description:
        Append rule to the local.rules

        Args:
            data (str): Data to be appended to the local.rules file
        """

        # Right now this is just a simple implementation

        if (rule := self.rule_translator(data)) is None:
            return

        if self.rule_exists(rule):
            return

        # Backup the rules file
        self.file_backup()

        # Append the rule to the rules file
        with open(self.rules_file, "a") as file:
            file.write(f"\n{rule}\n")

    def rule_exists(self, rule):
        """
        Description:
            Check if the rule already exists in the rules file
            This function reads the rules file line by line and determines if the
            provided rule is present in any of the lines. It is useful for avoiding
            duplicate entries in the rules file.

        Args:
            rule (str): Rule to be checked

        Returns:
            bool: True if the rule exists, False otherwise
        """

        # This needs to change if we are going to go with the pretty building of the rule

        with open(self.rules_file, "r") as file:
            rules = self.read_snort_rules(rules=file.readlines())
            # For now this function can't accurately check if a snort rule is duplicate,
            # because of the different sids

            # From the rule to add, create a temp without the sid
            temp_rule = self.read_snort_rule_no_sid(rule)

            # rules = list(map(self.rule_splitter, rules))
            # rule_obj = self.rule_splitter(rule)
            if any(rule in rule_line for rule_line in rules):
                return True
            return False

    def get_rules_from_file(self) -> list[str]:
        """
        Description:
            Get the rules from the rules file
            This function reads the rules file and returns a list of rules.
            It removes comments and empty lines from the rules.

        Returns:
            list[str]: List of rules from the rules file
        """
        with open(self.rules_file, "r") as file:
            return self.read_snort_rules(rules=file.readlines())

    def read_snort_rules(self, rules: list[str]) -> list[str]:
        """
        Processes a list of Snort rules and returns a list of valid rules.

        This method filters out comments, handles multi-line rules, and ensures
        that only properly formatted rules are included in the result.

        Args:
            rules (list[str]): A list of strings representing Snort rules.

        Returns:
            list[str]: A list of processed Snort rules. Single-line rules are
            included directly, while multi-line rules are concatenated into
            single strings.
        """

        # rules =
        result = []
        temp = []
        multi_line = False
        for rule in rules:
            # Remove comments and strip whitespace
            rule = rule.strip()
            if rule.startswith("#"):
                continue

            # This will only get the rules that are one lined
            if rule and rule.endswith(")") and rule != ")":
                result.append(rule)

            # This is going to start handling the rule as if it is in multiple lines
            elif rule and not rule.endswith(")") and rule != ")":
                temp.append(rule)
                multi_line = True
            # If the rule is multi-line and ends with a closing parenthesis, we join the temp list
            elif multi_line and rule.endswith(")"):
                temp.append(rule)
                result.append(" ".join(temp))
                temp = []
                multi_line = False

        return result

    def read_snort_rule_no_sid(self, rule: str, pretty: bool = False) -> str:
        """
        Description:
            Reads a Snort rule and removes the sid option.

        Args:
            rule (str): The Snort rule to be processed.

        Returns:
            str: The Snort rule without the sid option.
        """
        temp_rule = [
            part for part in rule.split("\n") if not part.strip().startswith("sid:")
        ]

        # There is a better way with the rule_splitter function
        if pretty:
            return "\n".join(temp_rule)
        return " ".join(temp_rule)

    def get_current_sid(self, start=10000, end=20000) -> int:
        """
        Description:
            Get the current Snort ID Version (sid) from the rules file.
            This function reads the rules file and extracts the sid from the first line.

        Returns:
            str: The current Snort ID Version (sid).
        """
        # Get all the rules

        rules = list(map(self.rule_splitter, self.get_rules_from_file()))
        # Get all the sids from the rules
        sids = list(map(lambda x: x.get("options", {}).get("sid"), rules))

        # Filter the sids to get the ones in the range
        filtered_sids = [int(sid) for sid in sids if start <= int(sid) <= end]
        current_sid = max(filtered_sids) + 1 if filtered_sids else start
        return current_sid

    def rule_splitter(self, rule: str) -> dict:
        """
        Description:
            Parses a Snort rule string and extracts its configurations into a dictionary.

        Args:
            rule (str): The Snort rule string to be parsed.

        Returns:
            dict: A dictionary containing the parsed configurations of the rule.
        """
        # Initialize the result dictionary
        parsed_rule = {}

        # Split the rule into header and options
        header, options = rule.split("(", 1)
        options = options.rstrip(")")

        # Parse the header
        header_parts = header.strip().split()
        if len(header_parts) >= 6:
            parsed_rule["action"] = header_parts[0]
            parsed_rule["protocol"] = header_parts[1]
            parsed_rule["src_ip"] = header_parts[2]
            parsed_rule["src_port"] = header_parts[3]
            parsed_rule["direction"] = header_parts[4]
            parsed_rule["dst_ip"] = header_parts[5]
            parsed_rule["dst_port"] = (
                header_parts[6] if len(header_parts) > 6 else "any"
            )

        # Parse the options
        options_dict = {}
        for option in options.split(";"):
            if ":" in option:
                key, value = option.split(":", 1)
                options_dict[key.strip()] = value.strip()
            elif option.strip():
                options_dict[option.strip()] = True

        parsed_rule["options"] = options_dict

        return parsed_rule

    def clear_snort_rules(self) -> bool:
        """
        Description:
            Clear the rules file
        """
        # Backup the rules file
        self.file_backup()
        self.save_file_content(self.rules_file, "")

        return True

    def show_snort_rules(self) -> str:
        """
        Description:
            Show the rules file content
        """
        rules = self.get_file_content(self.rules_file)
        return rules.split("\n\n")


if __name__ == "__main__":
    snorty = ManagerSnort()
    domain = "training.testserver.gr"
    domain = "forbidden.url"
    content = "74 72 61 69 6e 69 6e 67 2e 74 65 73 74 73 65 72 76 65 72 2e 67 72"
    # snorty.building_rule_block_domain(domain, verbose=True)
    snorty.building_rule_block(domain, verbose=True)
    # print(snorty.get_rules_from_file())
    # snorty.building_rule_block_icmp("10.45.0.3", verbose=True)
    # snorty.building_rule_alert_icmp("10.45.0.3", verbose=True)
