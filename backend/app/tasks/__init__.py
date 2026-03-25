"""
Celery async tasks - background job processing.

Tasks are queued by routes and processed by Celery workers.
They handle long-running operations like file generation.
"""

try:
    from tasks.generation_tasks import (
        generate_assignment_async,
        generate_presentation_async,
    )
except ImportError:
    generate_assignment_async = None
    generate_presentation_async = None

try:
    from tasks.export_tasks import (
        export_assignment_pdf,
        export_presentation_pptx,
    )
except ImportError:
    export_assignment_pdf = None
    export_presentation_pptx = None

__all__ = [
    "generate_assignment_async",
    "generate_presentation_async",
    "export_assignment_pdf",
    "export_presentation_pptx",
]
