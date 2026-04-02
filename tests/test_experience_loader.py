from job_agent.experience.loader import ExperienceLakeLoader


def test_loader_reads_example_lake():
    loader = ExperienceLakeLoader("data/experience_lake.example.json")
    lake = loader.load()

    assert lake.owner_name == "Jane Candidate"
    assert len(lake.experiences) == 1

    docs = loader.to_documents(lake)
    assert len(docs) == 1
    assert docs[0].metadata["experience_id"] == "exp_001"
