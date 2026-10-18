package tn.herwell.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

@Entity
@Table(name = "cycle_tracking")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CycleTracking {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "period_start_date", nullable = false)
    private LocalDate periodStartDate;
    
    @Column(name = "cycle_length_days")
    private Integer cycleLengthDays;
    
    @Column(columnDefinition = "TEXT")
    private String notes;
    
    @Column(name = "tracking_enabled", nullable = false)
    private Boolean trackingEnabled = false;
}
