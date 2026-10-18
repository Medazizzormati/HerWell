package tn.herwell.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.herwell.model.Resource;

@Repository
public interface ResourceRepository extends JpaRepository<Resource, Long> {
}
