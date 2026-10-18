package tn.herwell.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.herwell.model.SymptomLog;

@Repository
public interface SymptomLogRepository extends JpaRepository<SymptomLog, Long> {
}
