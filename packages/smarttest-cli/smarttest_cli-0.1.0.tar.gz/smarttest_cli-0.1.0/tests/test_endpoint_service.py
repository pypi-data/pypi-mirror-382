import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import Base, EndpointDB, ScenarioDB, EndpointParametersDB, ObjectDefinitionDB
from database.schemas import Endpoint, EndpointBase, Scenario, ScenarioBase, ObjectDefinitionBase
from service.EndpointService import (
    create_new_endpoint,
    create_scenario_parameter_if_needed,
    override_scenarios,
    get_endpoint_by_id
)


# Setup in-memory SQLite database for testing
@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def mock_endpoint_schema():
    """Create a mock endpoint schema for testing"""
    return EndpointBase(
        method="GET",
        endpoint="/test",
        raw_definition={"path": "/test", "method": "get"},
        scenarios=[],
        definitions=[],
        definitions_for_params=[],
        definitions_for_responses=[]
    )


@pytest.fixture
def mock_scenario_schema():
    """Create a mock scenario schema for testing"""
    return ScenarioBase(
        name="Test Scenario"
    )

@pytest.fixture
def mock_scenario():
    """Create a mock scenario for testing"""
    return Scenario(
        id=1,
        name="Test Scenario"
    )


@pytest.fixture
def mock_error_scenario_schema():
    """Create a mock error scenario schema for testing"""
    return ScenarioBase(
        name="Error Scenario"
    )


def test_get_endpoint_by_id_existing(db_session):
    """Test retrieving an existing endpoint by ID"""
    # Create a test endpoint in the database
    endpoint_db = EndpointDB(
        method="GET",
        endpoint="/test",
        raw_definition={"path": "/test", "method": "get"}
    )
    db_session.add(endpoint_db)
    db_session.commit()
    db_session.refresh(endpoint_db)
    
    # Retrieve the endpoint
    result = get_endpoint_by_id(db_session, endpoint_db.id)
    
    # Verify the result
    assert result is not None
    assert result.id == endpoint_db.id
    assert result.method == "GET"
    assert result.endpoint == "/test"
    assert result.raw_definition == {"path": "/test", "method": "get"}


def test_get_endpoint_by_id_nonexistent(db_session):
    """Test retrieving a non-existent endpoint by ID"""
    # Try to retrieve a non-existent endpoint
    result = get_endpoint_by_id(db_session, 999)
    
    # Verify the result is None
    assert result is None


@patch('service.EndpointService.create_new_object_definition')
@patch('service.EndpointService.create_new_scenario')
@patch('service.EndpointService.create_multiple_endpoint_parameter')
def test_create_new_endpoint_basic(
    mock_create_params, mock_create_scenario, mock_create_obj_def, db_session, mock_endpoint_schema
):
    """Test creating a new endpoint with basic properties"""
    # Set up mocks
    mock_create_params.return_value = []
    mock_create_scenario.return_value = []
    mock_create_obj_def.return_value = []

    endpoint_schema = Endpoint(
        id=1,
        default_success_endpoint_parameters=[],
        method=mock_endpoint_schema.method,
        endpoint=mock_endpoint_schema.endpoint,
        raw_definition=mock_endpoint_schema.raw_definition,
        scenarios=[],
        definitions=[],
        definitions_for_params=[],
        definitions_for_responses=[]
    )
    
    # Call the function
    result = create_new_endpoint(db_session, endpoint_schema)
    
    # Verify the result
    assert result is not None
    assert result.method == mock_endpoint_schema.method
    assert result.endpoint == mock_endpoint_schema.endpoint
    assert result.raw_definition == mock_endpoint_schema.raw_definition
    
    # Verify the endpoint was added to the database
    db_endpoint = get_endpoint_by_id(db_session, result.id)
    assert db_endpoint is not None
    assert db_endpoint.id == result.id


@patch('service.EndpointService.create_new_object_definition')
@patch('service.EndpointService.create_new_scenario')
@patch('service.EndpointService.create_multiple_endpoint_parameter')
def test_create_new_endpoint_with_definitions(
    mock_create_params, mock_create_scenario, mock_create_obj_def, db_session, mock_endpoint_schema
):
    """Test creating a new endpoint with object definitions"""
    # Create a mock definition
    mock_definition = ObjectDefinitionBase(
        key="TestDefinition",
        definition={"type": "object", "properties": {"name": {"type": "string"}}},
        is_param_definition=False
    )
    
    # Create a new endpoint schema with the definition
    endpoint_schema = EndpointBase(
        method=mock_endpoint_schema.method,
        endpoint=mock_endpoint_schema.endpoint,
        raw_definition=mock_endpoint_schema.raw_definition,
        scenarios=[],
        definitions=[mock_definition],
        definitions_for_params=[],
        definitions_for_responses=[]
    )
    
    # Set up mocks using real DB model objects
    mock_obj_def_db = ObjectDefinitionDB(
        id=1,
        key="TestDefinition",
        definition={"type": "object", "properties": {"name": {"type": "string"}}},
        is_param_definition=False
    )
    mock_create_params.return_value = []
    mock_create_scenario.return_value = []
    mock_create_obj_def.return_value = mock_obj_def_db
    
    # Call the function
    result = create_new_endpoint(db_session, endpoint_schema)
    
    # Ensure object definition creation was invoked
    assert mock_create_obj_def.called
    
    # Verify the result
    assert result is not None
    assert result.method == mock_endpoint_schema.method
    assert result.endpoint == mock_endpoint_schema.endpoint


@patch('service.EndpointService.create_new_object_definition')
@patch('service.EndpointService.create_new_scenario')
@patch('service.EndpointService.create_multiple_endpoint_parameter')
def test_create_new_endpoint_with_scenarios(
    mock_create_params, mock_create_scenario, mock_create_obj_def, db_session, mock_endpoint_schema, mock_scenario_schema
):
    """Test creating a new endpoint with scenarios"""

    # Create a mock definition
    mock_definition = ObjectDefinitionBase(
        key="TestDefinition",
        definition={"type": "object", "properties": {"name": {"type": "string"}}},
        is_param_definition=False
    )

    mock_obj_def_db = ObjectDefinitionDB(
        id=1,
        key="TestDefinition",
        definition={"type": "object", "properties": {"name": {"type": "string"}}},
        is_param_definition=False
    )

    # Create a new endpoint schema with the scenario
    endpoint_schema = EndpointBase(
        method=mock_endpoint_schema.method,
        endpoint=mock_endpoint_schema.endpoint,
        raw_definition=mock_endpoint_schema.raw_definition,
        scenarios=[mock_scenario_schema],
        definitions=[mock_definition],
        definitions_for_params=[],
        definitions_for_responses=[]
    )
    
    # Set up mocks
    mock_scenario_db = ScenarioDB(
        id=1,
        name="Test Scenario",
        requires_auth=False
    )
    
    mock_create_params.return_value = []
    mock_create_scenario.return_value = mock_scenario_db
    mock_create_obj_def.return_value = mock_obj_def_db
    
    # Call the function
    result = create_new_endpoint(db_session, endpoint_schema)
    
    # Verify calls happened
    assert mock_create_obj_def.called
    assert mock_create_scenario.called
    
    # Verify the result
    assert result is not None
    assert result.method == mock_endpoint_schema.method
    assert result.endpoint == mock_endpoint_schema.endpoint


def test_create_new_endpoint_with_parameters(db_session, mock_endpoint_schema):
    """Test creating a new endpoint with parameters"""
    # Use a real function call with patching at a lower level
    with patch('service.EndpointService.create_multiple_endpoint_parameter') as mock_create_params:
        # Set up mocks for parameters
        mock_param_db = EndpointParametersDB(
            parameter_name="test_param",
            parameter_type="PARAM_TYPE_PATH",
            default_schema_value=None,
            default_value="default_value"
        )
        mock_create_params.return_value = [mock_param_db]
        
        # Call the function
        result = create_new_endpoint(db_session, mock_endpoint_schema)
        
        # Verify parameter creation was called
        assert mock_create_params.called
        assert result is not None
    
    # Verify the result
    assert result is not None
    assert result.method == mock_endpoint_schema.method
    assert result.endpoint == mock_endpoint_schema.endpoint
    assert len(result.default_success_endpoint_parameters) > 0


@patch('service.EndpointService.create_new_scenario_parameter')
@patch('service.EndpointService.get_endpoint_parameter')
def test_create_scenario_parameter_if_needed_body_error(
    mock_get_param, mock_create_param, db_session, mock_endpoint_schema
):
    """Test creating scenario parameters for body error scenarios"""
    # Create a mock endpoint with ID
    endpoint = Endpoint(
        id=1,
        method=mock_endpoint_schema.method,
        endpoint=mock_endpoint_schema.endpoint,
        raw_definition=mock_endpoint_schema.raw_definition,
        scenarios=[],
        definitions=[],
        definitions_for_params=[],
        definitions_for_responses=[],
        default_success_endpoint_parameters=[]
    )
    
    # Create a mock scenario with body error
    mock_error_scenario_db = ScenarioDB(
        id=1,
        name="Error Scenario",
        error_in="body",
        error_type="missing",
        error_attribute="name",
        error_description="Name is required",
        requires_auth=False,
        scenario_parameters=[]
    )
    
    # Set up mocks
    mock_param = MagicMock()
    mock_param.id = 1
    mock_param.default_schema_value = {"name": "test"}
    mock_get_param.return_value = mock_param
    
    mock_error_body = {"error": "test"}
    with patch('service.EndpointService.create_body_for_error_scenario') as mock_create_body:
        mock_create_body.return_value = mock_error_body
    
        mock_scenario_param = MagicMock()
        mock_create_param.return_value = mock_scenario_param
        
        # Call the function
        create_scenario_parameter_if_needed(db_session, mock_error_scenario_db, endpoint)
        
        # Verify the mocks were called correctly
        mock_get_param.assert_called_once_with(db_session, endpoint.id, "body", "body")
        mock_create_body.assert_called_once()
        mock_create_param.assert_called_once()
        
        # Verify scenario parameters were added
        assert len(mock_error_scenario_db.scenario_parameters) == 1
        assert mock_error_scenario_db.scenario_parameters[0] == mock_scenario_param


@patch('service.EndpointService.create_new_scenario_parameter')
@patch('service.EndpointService.get_endpoint_parameter')
def test_create_scenario_parameter_if_needed_query_error(
    mock_get_param, mock_create_param, db_session, mock_endpoint_schema
):
    """Test creating scenario parameters for query parameter error scenarios"""
    # Create a mock endpoint with ID
    endpoint = Endpoint(
        id=1,
        method=mock_endpoint_schema.method,
        endpoint=mock_endpoint_schema.endpoint,
        raw_definition=mock_endpoint_schema.raw_definition,
        scenarios=[],
        definitions=[],
        definitions_for_params=[],
        definitions_for_responses=[],
        default_success_endpoint_parameters=[]
    )
    
    # Create a mock scenario with query error
    scenario = ScenarioDB(
        id=1,
        name="Error Scenario",
        error_in="query",
        error_type="invalid",
        error_attribute="id",
        error_description="ID must be a number",
        requires_auth=False,
        scenario_parameters=[]
    )
    
    # Set up mocks
    mock_param = MagicMock()
    mock_param.id = 1
    mock_get_param.return_value = mock_param
    
    mock_scenario_param = MagicMock()
    mock_create_param.return_value = mock_scenario_param
    
    # Call the function
    create_scenario_parameter_if_needed(db_session, scenario, endpoint)
    
    # Verify the mocks were called correctly
    mock_get_param.assert_called_once_with(db_session, endpoint.id, "id", "query")
    mock_create_param.assert_called_once()
    
    # Verify scenario parameters were added
    assert len(scenario.scenario_parameters) == 1
    assert scenario.scenario_parameters[0] == mock_scenario_param


def test_override_scenarios(db_session, mock_scenario):
    """Test overriding scenarios for an endpoint"""
    # Create a test endpoint in the database
    endpoint_db = EndpointDB(
        method="GET",
        endpoint="/test",
        raw_definition={"path": "/test", "method": "get"}
    )
    db_session.add(endpoint_db)
    db_session.commit()
    db_session.refresh(endpoint_db)
    
    # Create a simplified endpoint object with ID
    endpoint_dict = {
        "id": endpoint_db.id,
        "method": endpoint_db.method,
        "endpoint": endpoint_db.endpoint,
        "raw_definition": endpoint_db.raw_definition,
        "scenarios": [mock_scenario],
        "definitions": [],
        "definitions_for_params": [],
        "definitions_for_responses": []
    }
    
    # Use a real function call with patching at a lower level
    with patch('service.EndpointService.create_new_scenario') as mock_create_scenario:
        with patch('service.EndpointService.create_scenario_parameter_if_needed'):
            mock_scenario_dict = dict(
                id=1,
                name=mock_scenario.name,
                requires_auth=mock_scenario.requires_auth
            )
            mock_create_scenario.return_value = ScenarioDB(
                id=1,
                name=mock_scenario.name,
                requires_auth=mock_scenario.requires_auth
            )
            
            endpoint = Endpoint(**endpoint_dict)
            result = override_scenarios(db_session, endpoint)
            
            # Verify scenario creation was called
            assert mock_create_scenario.called
            assert result is not None
        
    # Verify the result
    assert result is not None
    assert result.id == endpoint_db.id


def test_override_scenarios_nonexistent_endpoint(db_session, mock_endpoint_schema):
    """Test overriding scenarios for a non-existent endpoint"""
    # Create a modified endpoint schema with an ID
    endpoint_schema = Endpoint(
        id=999,
        method=mock_endpoint_schema.method,
        endpoint=mock_endpoint_schema.endpoint,
        raw_definition=mock_endpoint_schema.raw_definition,
        scenarios=[],
        definitions=[],
        definitions_for_params=[],
        definitions_for_responses=[],
        default_success_endpoint_parameters=[]
    )
    
    # Call the function and expect an exception
    with pytest.raises(ValueError, match=f"Cannot find Endpoint with id {endpoint_schema.id}"):
        override_scenarios(db_session, endpoint_schema)
