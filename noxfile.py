import nox


@nox.session(python=["3.9", "3.10", "3.11", "3.12"])
def snakemake7(session):
    """Test Snakemake 7"""
    session.install("snakemake<8", "pulp<2.8", "pytest", ".")
    session.run("pytest")
    session.run("bash", "tests/run_tests.sh", external=True)


@nox.session(python=["3.12"])
def snakemake8(session):
    """Test Snakemake 8"""
    session.install("snakemake<9", "pytest", ".")
    session.run("pytest")
    session.run("bash", "tests/run_tests.sh", external=True)
