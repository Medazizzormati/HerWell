package tn.herwell.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import tn.herwell.model.StudyTask;
import tn.herwell.repository.StudyTaskRepository;

import java.util.List;

@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class TaskController {
    
    private final StudyTaskRepository taskRepository;
    
    @GetMapping
    public List<StudyTask> getAllTasks() {
        return taskRepository.findAll();
    }
    
    @PostMapping
    public StudyTask createTask(@RequestBody StudyTask task) {
        return taskRepository.save(task);
    }
    
    @PatchMapping("/{id}")
    public ResponseEntity<StudyTask> updateTask(@PathVariable Long id, @RequestBody StudyTask updates) {
        return taskRepository.findById(id)
            .map(task -> {
                if (updates.getTitle() != null) task.setTitle(updates.getTitle());
                if (updates.getSubject() != null) task.setSubject(updates.getSubject());
                if (updates.getDurationMinutes() != null) task.setDurationMinutes(updates.getDurationMinutes());
                if (updates.getPriority() != null) task.setPriority(updates.getPriority());
                if (updates.getCompleted() != null) task.setCompleted(updates.getCompleted());
                return ResponseEntity.ok(taskRepository.save(task));
            })
            .orElse(ResponseEntity.notFound().build());
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id) {
        if (taskRepository.existsById(id)) {
            taskRepository.deleteById(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
