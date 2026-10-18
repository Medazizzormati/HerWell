package tn.herwell.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

@Entity
@Table(name = "symptom_logs")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SymptomLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "log_date", nullable = false)
    private LocalDate logDate;
    
    @Column(columnDefinition = "TEXT")
    private String physicalSymptoms;
    
    @Column(columnDefinition = "TEXT")
    private String mood;
    
    private Integer energy;
    
    private Integer painLevel;
    
    @Column(columnDefinition = "TEXT")
    private String notes;
    
    @Column(name = "tracking_enabled", nullable = false)
    private Boolean trackingEnabled = false;
}
