package tn.herwell.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import tn.herwell.model.MoodCheckin;

@Repository
public interface MoodCheckinRepository extends JpaRepository<MoodCheckin, Long> {
}
