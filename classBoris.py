from enum import Enum,unique

@unique
class Scenario(str, Enum):
    default = "1"
    toto = "2"
    tata = "3"
class Batiment(object):
    __slots__ = ['scenario']
    def __init__(self):
        self.scenario = Scenario.default

    def getScenario(self):
        return self.scenario.name, self.scenario.value

    def setScenario(self, scenario: Scenario):
        self.scenario = scenario
        return
if __name__ == '__main__':
    sen =Scenario.toto
    bat = Batiment()
    bat.setScenario(Scenario.default)
    print(bat.getScenario())