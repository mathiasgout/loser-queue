from src import extract_data


if __name__ == "__main__":
    extract_data.create_json_file(
        tiers=["CHALLENGER", "GRANDMASTER", "MASTER"], number_of_matches_by_tier=300
    )
