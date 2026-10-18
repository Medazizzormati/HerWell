package tn.herwell.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.herwell.model.CycleTracking;

@Repository
public interface CycleTrackingRepository extends JpaRepository<CycleTracking, Long> {
}
