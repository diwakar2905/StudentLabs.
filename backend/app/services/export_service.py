"""
Export service - business logic for file export operations.
Handles PDF/PPT export and file management.
"""

from sqlalchemy.orm import Session
from app.models import Project, Assignment, Presentation, Export
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Service for export operations"""
    
    @staticmethod
    def create_export_record(
        db: Session,
        project_id: int,
        file_type: str,
        file_path: str,
        file_size: Optional[int] = None
    ) -> Export:
        """
        Create an export record
        
        Args:
            db: Database session
            project_id: Project ID
            file_type: Type of export (pdf, pptx)
            file_path: Path where file is stored
            file_size: Size of export file in bytes
            
        Returns:
            Created Export object
        """
        export = Export(
            project_id=project_id,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size
        )
        db.add(export)
        db.commit()
        db.refresh(export)
        
        logger.info(f"Created export record: {file_path} ({file_type})")
        return export
    
    @staticmethod
    def get_export(db: Session, export_id: int) -> Optional[Dict]:
        """Get export by ID"""
        export = db.query(Export).filter(Export.id == export_id).first()
        
        if not export:
            return None
        
        return {
            "id": export.id,
            "file_type": export.file_type,
            "file_path": export.file_path,
            "file_url": export.file_url,
            "file_size": export.file_size,
            "created_at": export.created_at
        }
    
    @staticmethod
    def list_project_exports(db: Session, project_id: int) -> list:
        """List all exports for a project"""
        exports = db.query(Export).filter(Export.project_id == project_id).all()
        
        return [
            {
                "id": e.id,
                "file_type": e.file_type,
                "file_path": e.file_path,
                "file_size": e.file_size,
                "created_at": e.created_at
            }
            for e in exports
        ]
    
    @staticmethod
    def delete_export(db: Session, export_id: int) -> bool:
        """Delete an export record"""
        export = db.query(Export).filter(Export.id == export_id).first()
        
        if not export:
            return False
        
        db.delete(export)
        db.commit()
        
        logger.info(f"Deleted export record: {export_id}")
        return True
    
    @staticmethod
    def get_pdf_export(db: Session, project_id: int) -> Optional[Dict]:
        """Get the most recent PDF export for a project"""
        export = db.query(Export).filter(
            Export.project_id == project_id,
            Export.file_type == "pdf"
        ).order_by(Export.created_at.desc()).first()
        
        if not export:
            return None
        
        return ExportService.get_export(db, export.id)
    
    @staticmethod
    def get_pptx_export(db: Session, project_id: int) -> Optional[Dict]:
        """Get the most recent PPTX export for a project"""
        export = db.query(Export).filter(
            Export.project_id == project_id,
            Export.file_type == "pptx"
        ).order_by(Export.created_at.desc()).first()
        
        if not export:
            return None
        
        return ExportService.get_export(db, export.id)
