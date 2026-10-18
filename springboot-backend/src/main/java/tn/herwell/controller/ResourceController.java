package tn.herwell.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import tn.herwell.model.Resource;
import tn.herwell.repository.ResourceRepository;

import java.util.List;

@RestController
@RequestMapping("/api/resources")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ResourceController {
    
    private final ResourceRepository resourceRepository;
    
    @GetMapping
    public List<Resource> getAllResources() {
        return resourceRepository.findAll();
    }
}
