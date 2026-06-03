"""
Example script demonstrating how to use the DevSecOps Deployment Gatekeeper.
"""
import sys
import os

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from devops_deployment_security_gate.core.orchestrator import SecurityGateOrchestrator

def main():
    """Example usage of the SecurityGateOrchestrator."""
    # Initialize the orchestrator
    orchestrator = SecurityGateOrchestrator()
    
    # Check system status
    print("Checking system status...")
    status = orchestrator.get_system_status()
    print(f"System status: {status['status']}")
    
    # Example: Run a security check on a pull request
    # Note: This will fail if you don't have valid credentials in your .env file
    print("\nRunning security check example...")
    result = orchestrator.run_security_check(
        pr_number="123",
        repository="example-org/example-repo",
        branch_name="feature-security-fix"
    )
    
    print("Security check result:")
    print(result)
    
    # Example: Run batch security checks
    print("\nRunning batch security checks example...")
    pr_list = [
        {
            "pr_number": "123",
            "repository": "example-org/example-repo",
            "branch_name": "feature-security-fix"
        },
        {
            "pr_number": "124",
            "repository": "example-org/example-repo",
            "branch_name": "bugfix-authentication"
        }
    ]
    
    batch_result = orchestrator.run_batch_security_checks(pr_list)
    print(f"Batch check completed: {batch_result['successful_checks']}/{batch_result['total_checks']} successful")

if __name__ == "__main__":
    main()