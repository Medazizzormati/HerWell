package tn.herwell.config;

import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import tn.herwell.model.MoodCheckin;
import tn.herwell.model.StudyTask;
import tn.herwell.repository.MoodCheckinRepository;
import tn.herwell.repository.StudyTaskRepository;

@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {
    
    private final StudyTaskRepository taskRepository;
    private final MoodCheckinRepository checkinRepository;
    
    @Override
    public void run(String... args) {
        // Seed initial data if empty
        if (taskRepository.count() == 0) {
            StudyTask task1 = new StudyTask();
            task1.setTitle("Review database joins");
            task1.setSubject("SQL");
            task1.setDurationMinutes(45);
            task1.setPriority("high");
            task1.setCompleted(false);
            taskRepository.save(task1);
            
            StudyTask task2 = new StudyTask();
            task2.setTitle("Practice React hooks");
            task2.setSubject("React");
            task2.setDurationMinutes(30);
            task2.setPriority("medium");
            task2.setCompleted(true);
            taskRepository.save(task2);
        }
        
        if (checkinRepository.count() == 0) {
            MoodCheckin checkin = new MoodCheckin();
            checkin.setMood("okay");
            checkin.setStress(3);
            checkin.setEnergy(3);
            checkin.setNote("Feeling okay today");
            checkinRepository.save(checkin);
        }
    }
}
