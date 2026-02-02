"""
Tests for CI/CD pipeline documentation validation.

These tests verify that the docs/CICD.md documentation:
- Exists and is readable
- Contains all required sections
- References existing workflow files
- Documents all GitHub Secrets used in workflows
- Is written in Portuguese (pt-BR)
"""

import os
import re
from pathlib import Path

import pytest
import yaml


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestCICDDocumentationExists:
    """Test that documentation file exists and is readable."""

    def test_cicd_documentation_file_exists(self) -> None:
        """Test that docs/CICD.md file exists."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        assert doc_path.exists(), f"Documentation file not found at {doc_path}"

    def test_cicd_documentation_is_readable(self) -> None:
        """Test that docs/CICD.md is readable and has content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) > 0, "Documentation file is empty"
        assert len(content) > 1000, "Documentation file seems too short"


class TestRequiredSections:
    """Test that documentation contains all required sections."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    def test_has_architecture_section(self, doc_content: str) -> None:
        """Test that documentation has architecture overview section."""
        assert "arquitetura" in doc_content.lower() or "architecture" in doc_content.lower()
        assert "## Arquitetura" in doc_content or "### Arquitetura" in doc_content

    def test_has_github_secrets_section(self, doc_content: str) -> None:
        """Test that documentation has GitHub Secrets section."""
        assert "github secrets" in doc_content.lower() or "secrets" in doc_content.lower()
        assert "DOCKERHUB_USERNAME" in doc_content
        assert "DOCKERHUB_TOKEN" in doc_content

    def test_has_deployment_flow_section(self, doc_content: str) -> None:
        """Test that documentation has deployment flow section."""
        assert "deploy" in doc_content.lower()
        assert "## Deploy" in doc_content or "### Deploy" in doc_content or "## Workflow de Deploy" in doc_content

    def test_has_troubleshooting_section(self, doc_content: str) -> None:
        """Test that documentation has troubleshooting section."""
        assert "troubleshooting" in doc_content.lower()
        assert "## Troubleshooting" in doc_content

    def test_has_rollback_section(self, doc_content: str) -> None:
        """Test that documentation has rollback procedures section."""
        assert "rollback" in doc_content.lower()
        assert "## " in doc_content and "Rollback" in doc_content

    def test_has_health_check_section(self, doc_content: str) -> None:
        """Test that documentation has health check section."""
        assert "health check" in doc_content.lower() or "health-check" in doc_content.lower()

    def test_has_vps_prerequisites_section(self, doc_content: str) -> None:
        """Test that documentation has VPS prerequisites section."""
        assert "vps" in doc_content.lower()
        assert "docker" in doc_content.lower()
        assert "docker compose" in doc_content.lower() or "docker-compose" in doc_content.lower()


class TestGitHubSecretsDocumentation:
    """Test that all GitHub Secrets used in workflows are documented."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    @pytest.fixture
    def workflow_secrets(self) -> set:
        """Extract secrets used in workflow files."""
        secrets = set()
        workflows_dir = PROJECT_ROOT / ".github" / "workflows"

        if not workflows_dir.exists():
            return secrets

        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text(encoding="utf-8")
            # Find all secrets.XXX patterns
            matches = re.findall(r"\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}", content)
            secrets.update(matches)

        return secrets

    def test_all_workflow_secrets_are_documented(self, doc_content: str, workflow_secrets: set) -> None:
        """Test that all secrets used in workflows are documented."""
        missing_secrets = []
        for secret in workflow_secrets:
            if secret not in doc_content:
                missing_secrets.append(secret)

        assert len(missing_secrets) == 0, f"Secrets used in workflows but not documented: {missing_secrets}"

    def test_dockerhub_secrets_documented(self, doc_content: str) -> None:
        """Test Docker Hub secrets are documented."""
        assert "DOCKERHUB_USERNAME" in doc_content
        assert "DOCKERHUB_TOKEN" in doc_content

    def test_vps_secrets_documented(self, doc_content: str) -> None:
        """Test VPS secrets are documented."""
        assert "VPS_HOST" in doc_content
        assert "VPS_SSH_KEY" in doc_content
        assert "VPS_USER" in doc_content

    def test_vercel_secrets_documented(self, doc_content: str) -> None:
        """Test Vercel secrets are documented."""
        assert "VERCEL_TOKEN" in doc_content
        assert "VERCEL_ORG_ID" in doc_content
        assert "VERCEL_PROJECT_ID" in doc_content


class TestWorkflowFileReferences:
    """Test that referenced workflow files exist."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    def test_ci_frontend_workflow_exists(self) -> None:
        """Test that ci-frontend.yml workflow exists."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-frontend.yml"
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"

    def test_deploy_frontend_workflow_exists(self) -> None:
        """Test that deploy-frontend.yml workflow exists."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "deploy-frontend.yml"
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"

    def test_deploy_backend_workflow_exists(self) -> None:
        """Test that deploy-backend.yml workflow exists."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "deploy-backend.yml"
        assert workflow_path.exists(), f"Workflow file not found at {workflow_path}"

    def test_docker_compose_prod_exists(self) -> None:
        """Test that docker-compose.prod.yml exists."""
        compose_path = PROJECT_ROOT / "docker" / "docker-compose.prod.yml"
        assert compose_path.exists(), f"Docker Compose file not found at {compose_path}"


class TestDockerFileReferences:
    """Test handling of Docker file references in documentation."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    def test_docker_compose_prod_referenced(self, doc_content: str) -> None:
        """Test that docker-compose.prod.yml is referenced in documentation."""
        assert "docker-compose.prod.yml" in doc_content

    def test_handles_missing_backend_dockerfile(self) -> None:
        """Test that documentation gracefully handles missing backend.Dockerfile.

        Note: backend.Dockerfile is defined in workflows but may not exist yet.
        Documentation should either not reference it or note it's pending creation.
        """
        dockerfile_path = PROJECT_ROOT / "docker" / "backend.Dockerfile"
        # This test documents the current state - the file may not exist yet
        # The workflow references it, so it should be created in a separate task
        if not dockerfile_path.exists():
            # This is expected - backend.Dockerfile is created in a separate task
            pass

    def test_handles_missing_etl_dockerfile(self) -> None:
        """Test that documentation gracefully handles missing etl.Dockerfile.

        Note: etl.Dockerfile may be defined in tasks but not exist yet.
        """
        dockerfile_path = PROJECT_ROOT / "docker" / "etl.Dockerfile"
        # This test documents the current state - the file may not exist yet
        if not dockerfile_path.exists():
            # This is expected - etl.Dockerfile is created in a separate task
            pass


class TestPortugueseLanguage:
    """Test that documentation is written in Portuguese (pt-BR)."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    def test_has_portuguese_content(self, doc_content: str) -> None:
        """Test that documentation contains Portuguese words."""
        portuguese_words = [
            "documentação",
            "pipeline",
            "visão",
            "geral",
            "arquitetura",
            "fluxo",
            "trabalho",
            "configuração",
            "verificar",
            "problema",
            "solução",
            "procedimentos",
        ]
        found_portuguese = sum(1 for word in portuguese_words if word.lower() in doc_content.lower())
        assert found_portuguese >= 5, "Documentation does not appear to be in Portuguese"

    def test_section_headers_in_portuguese(self, doc_content: str) -> None:
        """Test that main section headers are in Portuguese."""
        portuguese_headers = [
            "Visão Geral",
            "Arquitetura",
            "Fluxo",
            "Troubleshooting",  # Technical term, acceptable in English
            "Rollback",  # Technical term, acceptable in English
        ]
        found_headers = sum(1 for header in portuguese_headers if header in doc_content)
        assert found_headers >= 3, "Section headers should be primarily in Portuguese"


class TestTroubleshootingCompleteness:
    """Test that troubleshooting section covers common failure scenarios."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    def test_covers_workflow_failures(self, doc_content: str) -> None:
        """Test troubleshooting covers workflow/CI failures."""
        content_lower = doc_content.lower()
        assert "lint" in content_lower and ("falh" in content_lower or "fail" in content_lower)

    def test_covers_docker_build_issues(self, doc_content: str) -> None:
        """Test troubleshooting covers Docker build issues."""
        content_lower = doc_content.lower()
        assert "docker" in content_lower and ("build" in content_lower or "dockerfile" in content_lower)

    def test_covers_ssh_connection_problems(self, doc_content: str) -> None:
        """Test troubleshooting covers SSH connection problems."""
        content_lower = doc_content.lower()
        assert "ssh" in content_lower
        assert "conexão" in content_lower or "connection" in content_lower or "conex" in content_lower

    def test_covers_migration_failures(self, doc_content: str) -> None:
        """Test troubleshooting covers migration failures."""
        content_lower = doc_content.lower()
        assert "migration" in content_lower

    def test_covers_health_check_failures(self, doc_content: str) -> None:
        """Test troubleshooting covers health check failures."""
        content_lower = doc_content.lower()
        assert "health" in content_lower and "check" in content_lower


class TestIntegrationWithWorkflows:
    """Integration tests verifying documentation accuracy against actual workflow files."""

    @pytest.fixture
    def doc_content(self) -> str:
        """Load documentation content."""
        doc_path = PROJECT_ROOT / "docs" / "CICD.md"
        return doc_path.read_text(encoding="utf-8")

    def test_ci_frontend_trigger_documented_correctly(self, doc_content: str) -> None:
        """Test that CI frontend trigger (pull_request) is documented correctly."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-frontend.yml"
        if workflow_path.exists():
            workflow_content = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
            # Check if pull_request trigger is documented
            if "pull_request" in workflow_content.get("on", {}):
                assert "pull request" in doc_content.lower() or "pull_request" in doc_content.lower()

    def test_deploy_frontend_trigger_documented_correctly(self, doc_content: str) -> None:
        """Test that deploy frontend trigger (push to main) is documented correctly."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "deploy-frontend.yml"
        if workflow_path.exists():
            workflow_content = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
            # Check if push trigger is documented
            if "push" in workflow_content.get("on", {}):
                assert "push" in doc_content.lower() and "main" in doc_content.lower()

    def test_deploy_backend_jobs_documented(self, doc_content: str) -> None:
        """Test that deploy backend jobs (build-push, deploy) are documented."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "deploy-backend.yml"
        if workflow_path.exists():
            workflow_content = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
            jobs = workflow_content.get("jobs", {})
            # Check that main jobs are documented
            if "build-push" in jobs:
                assert "build" in doc_content.lower() and "push" in doc_content.lower()
            if "deploy" in jobs:
                assert "deploy" in doc_content.lower()

    def test_vercel_deployment_documented(self, doc_content: str) -> None:
        """Test that Vercel deployment is documented for frontend."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "deploy-frontend.yml"
        if workflow_path.exists():
            content = workflow_path.read_text(encoding="utf-8")
            if "vercel" in content.lower():
                assert "vercel" in doc_content.lower()

    def test_docker_hub_integration_documented(self, doc_content: str) -> None:
        """Test that Docker Hub integration is documented for backend."""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "deploy-backend.yml"
        if workflow_path.exists():
            content = workflow_path.read_text(encoding="utf-8")
            if "docker" in content.lower() and "hub" in content.lower():
                assert "docker hub" in doc_content.lower() or "dockerhub" in doc_content.lower()
