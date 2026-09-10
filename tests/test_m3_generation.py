from pathlib import Path

from simulation.generation.scenarios import generate_scenarios
from simulation.scenario import load_scenario


def test_generation_is_reproducible(tmp_path):
    a_dir = tmp_path / "a"
    b_dir = tmp_path / "b"

    a = generate_scenarios(10, seed=99, output_dir=a_dir)
    b = generate_scenarios(10, seed=99, output_dir=b_dir)

    assert [x.name for x in a] == [x.name for x in b]
    assert [x.initial for x in a] == [x.initial for x in b]
    assert [x.events for x in a] == [x.events for x in b]


def test_generated_scenarios_are_loadable(tmp_path):
    generate_scenarios(5, seed=1, output_dir=tmp_path)
    for path in tmp_path.glob("*.json"):
        scenario = load_scenario(path)
        assert scenario.duration_min > 0
        assert scenario.timestep_min > 0
