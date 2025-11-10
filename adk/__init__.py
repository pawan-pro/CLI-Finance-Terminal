class BaseAgent:
    def __init__(self):
        """Initialize the base agent"""
        self.name = self.__class__.__name__
        self.config = {}
        self.status = "initialized"

    def setup(self):
        """Setup method for any initialization logic"""
        pass

    def run(self, *args, **kwargs):
        """Run method that should be implemented by subclasses"""
        raise NotImplementedError("Subclasses should implement this method")

    def teardown(self):
        """Teardown method for cleanup logic"""
        pass
    
    def update_config(self, **kwargs):
        """Update agent configuration"""
        self.config.update(kwargs)

    def execute_with_error_handling(self, *args, **kwargs):
        """Execute the run method with error handling"""
        try:
            self.status = "running"
            result = self.run(*args, **kwargs)
            self.status = "completed"
            return result
        except Exception as e:
            self.status = "error"
            raise e