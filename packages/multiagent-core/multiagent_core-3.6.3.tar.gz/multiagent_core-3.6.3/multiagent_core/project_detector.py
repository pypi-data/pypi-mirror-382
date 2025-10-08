"""Smart project type detection for packaging setup."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import os


class ProjectTypeDetector:
    """Detects project type and recommends packaging strategy."""
    
    def __init__(self, project_path: Path):
        self.path = Path(project_path)
        self.indicators = self._load_indicators()
        
    def _load_indicators(self) -> Dict[str, Dict]:
        """Load project type indicators."""
        return {
            'python_cli': {
                'files': ['cli.py', '__main__.py', 'main.py'],
                'patterns': ['*.py', 'src/*.py'],
                'imports': ['click', 'argparse', 'typer'],
                'packaging': 'pipx',
                'templates': ['pyproject.toml', 'MANIFEST.in', 'VERSION']
            },
            'python_backend': {
                'files': ['app.py', 'server.py', 'api.py', 'wsgi.py'],
                'patterns': ['*.py', 'requirements.txt', 'Pipfile'],
                'imports': ['flask', 'django', 'fastapi', 'uvicorn'],
                'packaging': 'pip',
                'templates': ['pyproject.toml', 'requirements.txt', 'Dockerfile']
            },
            'node_frontend': {
                'files': ['package.json', 'index.js', 'app.js'],
                'patterns': ['*.js', '*.jsx', '*.ts', '*.tsx'],
                'frameworks': ['react', 'vue', 'angular', 'svelte'],
                'packaging': 'npm',
                'templates': ['package.json', '.npmrc', 'tsconfig.json']
            },
            'node_cli': {
                'files': ['bin/cli.js', 'cli.js'],
                'patterns': ['bin/*.js'],
                'packaging': 'npm',
                'templates': ['package.json', 'bin/cli.js']
            },
            'fullstack': {
                'indicators': ['python_backend', 'node_frontend'],
                'packaging': 'hybrid',
                'templates': ['pyproject.toml', 'package.json', 'docker-compose.yml']
            }
        }
    
    def detect(self) -> Tuple[str, Dict]:
        """
        Detect project type and return packaging recommendations.
        
        Returns:
            Tuple of (project_type, metadata)
        """
        scores = {}
        
        # Check for existing packaging files
        if (self.path / 'pyproject.toml').exists():
            scores['python'] = scores.get('python', 0) + 10
        if (self.path / 'package.json').exists():
            scores['node'] = scores.get('node', 0) + 10
            
        # Check file patterns
        py_files = list(self.path.glob('**/*.py'))
        js_files = list(self.path.glob('**/*.js')) + list(self.path.glob('**/*.ts'))
        
        if py_files:
            scores['python'] = scores.get('python', 0) + len(py_files)
            
            # Check for CLI patterns
            if any(f.name in ['cli.py', '__main__.py'] for f in py_files):
                scores['python_cli'] = scores.get('python_cli', 0) + 5
                
            # Check for backend patterns  
            if any(f.name in ['app.py', 'server.py', 'api.py'] for f in py_files):
                scores['python_backend'] = scores.get('python_backend', 0) + 5
                
        if js_files:
            scores['node'] = scores.get('node', 0) + len(js_files)
            
            # Check for CLI patterns
            if (self.path / 'bin').exists():
                scores['node_cli'] = scores.get('node_cli', 0) + 5
            else:
                scores['node_frontend'] = scores.get('node_frontend', 0) + 5
        
        # Determine primary type
        if not scores:
            return 'unknown', {'suggestion': 'No clear project type detected'}
            
        # Check for fullstack
        if scores.get('python', 0) > 5 and scores.get('node', 0) > 5:
            return 'fullstack', {
                'primary': 'python_backend',
                'secondary': 'node_frontend',
                'packaging': 'hybrid'
            }
        
        # Determine specific type
        if scores.get('python_cli', 0) > scores.get('python_backend', 0):
            return 'python_cli', {
                'packaging': 'pipx',
                'entry_point': self._find_entry_point()
            }
        elif scores.get('python_backend', 0) > 0:
            return 'python_backend', {
                'packaging': 'pip',
                'framework': self._detect_python_framework()
            }
        elif scores.get('node_cli', 0) > 0:
            return 'node_cli', {
                'packaging': 'npm',
                'global': True
            }
        elif scores.get('node_frontend', 0) > 0:
            return 'node_frontend', {
                'packaging': 'npm',
                'framework': self._detect_js_framework()
            }
            
        return 'unknown', scores
    
    def _find_entry_point(self) -> Optional[str]:
        """Find the CLI entry point for Python projects."""
        candidates = ['cli.py', '__main__.py', 'main.py']
        for candidate in candidates:
            if (self.path / candidate).exists():
                return candidate
        
        # Check in src/ or module directories
        for py_file in self.path.glob('**/cli.py'):
            return str(py_file.relative_to(self.path))
            
        return None
    
    def _detect_python_framework(self) -> Optional[str]:
        """Detect Python web framework."""
        req_files = [
            self.path / 'requirements.txt',
            self.path / 'Pipfile',
            self.path / 'pyproject.toml'
        ]
        
        frameworks = {
            'django': ['django'],
            'flask': ['flask'],
            'fastapi': ['fastapi', 'uvicorn'],
            'pyramid': ['pyramid'],
            'tornado': ['tornado']
        }
        
        for req_file in req_files:
            if req_file.exists():
                content = req_file.read_text().lower()
                for framework, indicators in frameworks.items():
                    if any(ind in content for ind in indicators):
                        return framework
                        
        return None
    
    def _detect_js_framework(self) -> Optional[str]:
        """Detect JavaScript framework."""
        pkg_json = self.path / 'package.json'
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                frameworks = {
                    'react': ['react', 'react-dom'],
                    'vue': ['vue'],
                    'angular': ['@angular/core'],
                    'svelte': ['svelte'],
                    'next': ['next'],
                    'nuxt': ['nuxt']
                }
                
                for framework, indicators in frameworks.items():
                    if any(ind in deps for ind in indicators):
                        return framework
            except:
                pass
                
        return None
    
    def generate_packaging_files(self, project_type: str, metadata: Dict) -> List[Dict]:
        """Generate appropriate packaging files based on project type."""
        files = []
        
        if project_type == 'python_cli':
            files.append({
                'path': 'pyproject.toml',
                'content': self._generate_pyproject_cli(metadata)
            })
            files.append({
                'path': 'VERSION',
                'content': json.dumps({
                    "version": "0.1.0",
                    "commit": "initial",
                    "build_date": "",
                    "build_type": "development"
                }, indent=2)
            })
            files.append({
                'path': 'MANIFEST.in',
                'content': "include VERSION\ninclude README.md\ninclude LICENSE\n"
            })
            
        elif project_type == 'python_backend':
            files.append({
                'path': 'pyproject.toml',
                'content': self._generate_pyproject_backend(metadata)
            })
            
        elif project_type in ['node_frontend', 'node_cli']:
            # Package.json should already exist for node projects
            pass
            
        elif project_type == 'fullstack':
            files.extend([
                {
                    'path': 'pyproject.toml',
                    'content': self._generate_pyproject_backend(metadata)
                },
                {
                    'path': 'docker-compose.yml',
                    'content': self._generate_docker_compose()
                }
            ])
        
        return files
    
    def _generate_pyproject_cli(self, metadata: Dict) -> str:
        """Generate pyproject.toml for CLI projects."""
        project_name = self.path.name.replace('_', '-')
        module_name = project_name.replace('-', '_')
        entry_point = metadata.get('entry_point', 'cli.py').replace('.py', '')
        
        return f'''[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "AI-powered {project_name} automation"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}}
]
dependencies = [
    "click>=8.0",
    "rich>=10.0",
]

[project.scripts]
{module_name} = "{module_name}.{entry_point}:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
    "black>=22.0",
    "mypy>=0.961",
]

[tool.setuptools.packages.find]
include = ["{module_name}*"]
exclude = ["tests*"]
'''
    
    def _generate_pyproject_backend(self, metadata: Dict) -> str:
        """Generate pyproject.toml for backend projects."""
        project_name = self.path.name.replace('_', '-')
        framework = metadata.get('framework', 'flask')
        
        deps = {
            'flask': 'flask>=2.0\nflask-cors>=3.0',
            'fastapi': 'fastapi>=0.68\nuvicorn[standard]>=0.15',
            'django': 'django>=4.0'
        }
        
        return f'''[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "{project_name} API service"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    {deps.get(framework, '')}
]

[tool.setuptools.packages.find]
include = ["{project_name.replace('-', '_')}*"]
'''
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for fullstack projects."""
        return '''version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
      
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''