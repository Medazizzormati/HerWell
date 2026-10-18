package tn.herwell.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import tn.herwell.model.Project;
import tn.herwell.repository.ProjectRepository;

import java.util.List;

@RestController
@RequestMapping("/api/projects")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ProjectController {
    
    private final ProjectRepository projectRepository;
    
    @GetMapping
    public List<Project> getAllProjects() {
        return projectRepository.findAll();
    }
    
    @PostMapping
    public Project createProject(@RequestBody Project project) {
        return projectRepository.save(project);
    }
    
    @PatchMapping("/{id}")
    public ResponseEntity<Project> updateProject(@PathVariable Long id, @RequestBody Project updates) {
        return projectRepository.findById(id)
            .map(project -> {
                if (updates.getTitle() != null) project.setTitle(updates.getTitle());
                if (updates.getDescription() != null) project.setDescription(updates.getDescription());
                if (updates.getTechnologies() != null) project.setTechnologies(updates.getTechnologies());
                if (updates.getStatus() != null) project.setStatus(updates.getStatus());
                return ResponseEntity.ok(projectRepository.save(project));
            })
            .orElse(ResponseEntity.notFound().build());
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProject(@PathVariable Long id) {
        if (projectRepository.existsById(id)) {
            projectRepository.deleteById(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
