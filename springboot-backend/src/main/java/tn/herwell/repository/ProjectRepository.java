package tn.herwell.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.herwell.model.Project;

@Repository
public interface ProjectRepository extends JpaRepository<Project, Long> {
}
