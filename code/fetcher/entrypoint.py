
print("Starting entrypoint...")
if __name__ == "__main__":
    import asyncio
    from src.tfg_fetcher.app import main


    # load_dotenv(override=True)
    asyncio.run(main())
