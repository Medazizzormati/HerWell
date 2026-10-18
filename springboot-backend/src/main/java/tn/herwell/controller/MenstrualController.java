package tn.herwell.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import tn.herwell.model.CycleTracking;
import tn.herwell.model.SymptomLog;
import tn.herwell.repository.CycleTrackingRepository;
import tn.herwell.repository.SymptomLogRepository;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/menstrual")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class MenstrualController {
    
    private final CycleTrackingRepository cycleRepository;
    private final SymptomLogRepository symptomRepository;
    
    @GetMapping("/cycles")
    public List<CycleTracking> getAllCycles() {
        return cycleRepository.findAll();
    }
    
    @PostMapping("/cycles")
    public CycleTracking createCycle(@RequestBody CycleTracking cycle) {
        return cycleRepository.save(cycle);
    }
    
    @DeleteMapping("/cycles/{id}")
    public ResponseEntity<Void> deleteCycle(@PathVariable Long id) {
        if (cycleRepository.existsById(id)) {
            cycleRepository.deleteById(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    @GetMapping("/symptoms")
    public List<SymptomLog> getAllSymptoms() {
        return symptomRepository.findAll();
    }
    
    @PostMapping("/symptoms")
    public SymptomLog createSymptomLog(@RequestBody SymptomLog symptom) {
        return symptomRepository.save(symptom);
    }
    
    @DeleteMapping("/symptoms/{id}")
    public ResponseEntity<Void> deleteSymptomLog(@PathVariable Long id) {
        if (symptomRepository.existsById(id)) {
            symptomRepository.deleteById(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    @GetMapping("/estimate-next-period")
    public ResponseEntity<Map<String, Object>> estimateNextPeriod() {
        List<CycleTracking> cycles = cycleRepository.findAll();
        if (cycles.size() < 2) {
            return ResponseEntity.ok(Map.of(
                "estimate", null,
                "message", "Need at least 2 recorded cycles to estimate next period"
            ));
        }
        
        // Simple estimation: use most recent cycle length
        CycleTracking lastCycle = cycles.get(cycles.size() - 1);
        if (lastCycle.getCycleLengthDays() == null) {
            return ResponseEntity.ok(Map.of(
                "estimate", null,
                "message", "Cycle length not recorded"
            ));
        }
        
        LocalDate lastPeriod = lastCycle.getPeriodStartDate();
        LocalDate nextEstimate = lastPeriod.plusDays(lastCycle.getCycleLengthDays());
        
        return ResponseEntity.ok(Map.of(
            "estimate", nextEstimate.toString(),
            "message", "This is an estimate based on your cycle history",
            "disclaimer", "This is not a medical prediction. Cycle dates can vary."
        ));
    }
    
    @DeleteMapping("/all-data")
    public ResponseEntity<Void> deleteAllData() {
        cycleRepository.deleteAll();
        symptomRepository.deleteAll();
        return ResponseEntity.noContent().build();
    }
}
