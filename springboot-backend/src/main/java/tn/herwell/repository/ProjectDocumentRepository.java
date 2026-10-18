package tn.herwell.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.herwell.model.ProjectDocument;

@Repository
public interface ProjectDocumentRepository extends JpaRepository<ProjectDocument, Long> {
}
