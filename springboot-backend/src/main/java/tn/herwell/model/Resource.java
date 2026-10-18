package tn.herwell.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "resources")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Resource {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String title;
    
    @Column(nullable = false)
    private String category;
    
    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;
    
    private String sourceLabel;
    
    private String sourceUrl;
    
    private String language;
    
    private String verificationStatus;
}
