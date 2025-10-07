from intuned_browser.intuned_services.api_gateways.ai_api_gateway import APIGateway


class GatewayFactory:
    """Factory class for creating pre-configured gateway instances"""

    @staticmethod
    def create_ai_gateway() -> APIGateway:
        """Create a gateway instance with optional configuration"""

        return APIGateway()
