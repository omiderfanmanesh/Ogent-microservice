"""
Fixed version of the create_agent method for the AgentService class.
This method properly handles configuration and config parameters.
"""

async def create_agent(
    self,
    name: str,
    description: str,
    agent_type: str,
    configuration: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    permissions: Optional[AgentPermissions] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> Agent:
    """
    Create a new agent.
    
    Args:
        name: Agent name
        description: Agent description
        agent_type: Type of agent
        configuration: Agent configuration (primary parameter)
        config: Agent configuration (legacy parameter)
        permissions: Agent permissions
        metadata: Additional metadata
        user_id: ID of the user who owns the agent
        
    Returns:
        Created agent
        
    Raises:
        ValueError: If the agent type is not supported or the configuration is invalid
    """
    # Use proper configuration (prioritize configuration over config)
    final_config = configuration if configuration is not None else config or {}
    
    # Validate agent type
    available_types = self.agent_factory.get_available_agent_types()
    if agent_type not in available_types:
        raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {', '.join(available_types)}")
    
    # Create default permissions if none provided
    if not permissions:
        permissions = AgentPermissions()
    
    # Create agent entity
    agent = Agent(
        name=name,
        description=description,
        agent_type=agent_type,
        configuration=final_config,
        permissions=permissions,
        metadata=metadata or {},
        user_id=user_id
    )
    
    # Validate configuration by creating an agent instance
    try:
        self.agent_factory.create_agent(
            agent_type=agent_type,
            configuration=final_config,
            permissions=permissions
        )
    except Exception as e:
        raise ValueError(f"Invalid agent configuration: {str(e)}")
    
    # Save agent to database
    created_agent = await self.agent_repository.create(agent)
    
    logger.info(f"Created agent '{name}' with ID {created_agent.id}")
    return created_agent 