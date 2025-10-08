from fileagent import FileAgent


def main():
    """
    Main function to run the FileAgent.
    """
    agent = FileAgent()
    agent.run_uvicorn()


if __name__ == "__main__":
    main()
