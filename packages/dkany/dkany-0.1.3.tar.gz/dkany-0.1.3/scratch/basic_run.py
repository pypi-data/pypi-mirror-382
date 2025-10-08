from dkany.client import DKANClient as DkanyClient

def main():
    client = DkanyClient(
        base_url = "https://edit.data.medicaid.gov"
    )

    test_dataset_id = "9e407144-9ed9-5cee-937a-17d65b07a9a7"

    exists = client.check_dataset_exists(test_dataset_id)

    print(f"dataset {exists} exits")

if __name__ == "__main__":
    main()