from dataclasses import dataclass, field
from random import randint, choice, uniform

@dataclass
class Variable:
    variable_name: str

    def initialize(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def revert(self):
        raise NotImplementedError
    
    @property
    def value(self):
        raise NotImplementedError
    
    def __str__(self) -> str:
        raise NotImplementedError

@dataclass
class ListBasedVariable(Variable):
    values: list
    value_names: list[str] = None
    current_idx: int = None
    previous_idx: int = None

    def __post_init__(self):
        if self.value_names == None:
            self.value_names = [str(x) for x in self.values]

        if self.current_idx == None:
            self.randomize()

    def randomize(self):
        """ Set the value to a random value
        """
        self.current_idx = randint(0, len(self.values)-1)

    def revert(self):
        """ Revert variable to the previous state

        Raises:
            ValueError: No previous state is available
        """
        if self.previous_idx == None:
            raise ValueError("No previous idx available")
        self.current_idx = self.previous_idx
        
    @property
    def value(self) -> list:
        return self.values[self.current_idx]
    
    def __str__(self) -> str:
        if self.current_idx == None:
            return f"Valiable {self.variable_name} is not yet initialized" 
        
        return f"{self.variable_name} \t=> {self.value_names[self.current_idx]}"


@dataclass
class DiscreteVariable(ListBasedVariable):
    def step(self):
        """ Make a step by either increasing, or decreasing the current index
        """

        self.previous_idx = self.current_idx
        if self.current_idx == 0:
            self.current_idx = 1
            return
        
        if self.current_idx == len(self.values)-1:
            self.current_idx = len(self.values)-2
            return

        self.current_idx = choice([self.current_idx - 1, 
                                   self.current_idx + 1])

@dataclass
class CategoricalVariable(ListBasedVariable):
    def step(self):
        """ Make a step by chosing a random new index
        """
        self.previous_idx = self.current_idx
        self.current_idx = choice([x for x in range(len(self.values)) if x != self.current_idx])

@dataclass
class ContinuousVariable(Variable):
    lower_bound: float
    upper_bound: float
    value: float = None
    previous_value: float = None

    @property
    def value(self) -> float:
        return self._value
    
    @value.setter
    def value(self, value: float):
        # Handle default value
        if isinstance(value, property):
            self.randomize_value()
            return 
        
        # Bound the value between upper and lower bound
        value = self.upper_bound if value > self.upper_bound else value
        value = self.lower_bound if value < self.lower_bound else value

        self._value = value

    def randomize_value(self):
        """ Set the value to a random value within the bounds
        """
        self.value = uniform(self.lower_bound, self.upper_bound)

    @property
    def max_step_size(self) -> float:
        return (self.upper_bound - self.lower_bound) / 10
    
    def step(self):
        """ Make a step by taking a step of a random size between -max_step and max_step. 
            max_step is 10% of the allowed range of the variable.
            With be capped to the bounds if it exceeds it
        """
        self.previous_value = self.value

        step_size = self.max_step_size
        direction = uniform(-step_size, step_size)

        self.value += direction

    def revert(self):
        """ Revert variable to the previous state

        Raises:
            ValueError: No previous state is available
        """
        if self.previous_value is None:
            raise ValueError("No previous value available")

        self.value = self.previous_value


