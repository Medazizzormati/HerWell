package tn.herwell.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import tn.herwell.model.MoodCheckin;
import tn.herwell.repository.MoodCheckinRepository;

import java.util.List;

@RestController
@RequestMapping("/api/checkins")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CheckinController {
    
    private final MoodCheckinRepository checkinRepository;
    
    @GetMapping
    public List<MoodCheckin> getAllCheckins() {
        return checkinRepository.findAll();
    }
    
    @PostMapping
    public MoodCheckin createCheckin(@RequestBody MoodCheckin checkin) {
        return checkinRepository.save(checkin);
    }
}
