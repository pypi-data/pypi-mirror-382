import logging
from typing import Annotated
import typer
import yaml

from champions.model.datacard import DataCard
from champions.model.settings import EvalSettings, TrainSettings
from champions.service.eval import Eval
from champions.service.train import Train


logger = logging.getLogger(__name__)

app = typer.Typer()


# def main(config: Annotated[typer.FileText, typer.Option()]):
@app.command()
def train(
    datacard: Annotated[typer.FileText, typer.Option()],
    trainsettings: Annotated[typer.FileText, typer.Option()],
):
    train = Train(
        dc=DataCard(**yaml.safe_load(datacard)),
        settings=TrainSettings(**yaml.safe_load(trainsettings)),
    )
    train.run()


@app.command()
def eval(
    datacard: Annotated[typer.FileText, typer.Option()],
    evalsettings: Annotated[typer.FileText, typer.Option()],
):
    train = Eval(
        dc=DataCard(**yaml.safe_load(datacard)),
        settings=EvalSettings(**yaml.safe_load(evalsettings)),
    )
    train.run()
