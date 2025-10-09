# Brynq Recruitee SDK

A Python SDK for interacting with the Recruitee API, providing a clean, modular interface to the Recruitee API with specialized modules for different aspects of the API.

## Installation

```bash
pip install brynq_sdk_recruitee
```

## Usage

```python
from brynq_sdk_recruitee import Recruitee, Candidates, Offers, Organization, Vacancies, Applicants

# Initialize the main client
recruitee_client = Recruitee(label='your_label')

# Candidates operations
candidates = Candidates(recruitee_client)
response = candidates.get_candidates()
print(response.json())

# Offers operations
offers = Offers(recruitee_client)
response = offers.get_offers()
print(response.json())

# Organization operations
organization = Organization(recruitee_client)
response = organization.get_departments()
print(response.json())
```

## Credentials

The credentials for accessing the Recruitee API are securely stored and managed within the BrynQ platform. You authorize yourself in the system by providing necessary details like the token and company ID directly in BrynQ. The SDK will automatically retrieve these credentials when you initialize the client.

## SDK Structure

The SDK is organized into several modules, each focused on a specific aspect of the Recruitee API:

- `recruitee.py`: Base client that provides low-level access to the Recruitee API
- `candidates.py`: Methods for managing candidates
- `offers.py`: Methods for managing offers/vacancies
- `organization.py`: Methods for retrieving organizational data (locations, departments, etc.)
- `vacancies.py`: Legacy methods for managing vacancies (delegates to Offers)
- `applicants.py`: Methods for managing applicants
- `rehire_check.py`: Methods for checking rehire status (delegates to Candidates)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the BrynQ License. 