import React, { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, Calendar, Clock, Plus, Trash2 } from "lucide-react";
import "./Calendar.css";

export default function ProfessionalCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [newEvent, setNewEvent] = useState({ title: "", time: "", type: "study" });

  // Load events from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("herwell-calendar-events");
    if (saved) {
      setEvents(JSON.parse(saved));
    }
  }, []);

  // Save events to localStorage
  useEffect(() => {
    localStorage.setItem("herwell-calendar-events", JSON.stringify(events));
  }, [events]);

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();
    
    const days = [];
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    return days;
  };

  const getEventsForDate = (date) => {
    if (!date) return [];
    const dateStr = date.toISOString().split('T')[0];
    return events.filter(e => e.date === dateStr);
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const addEvent = () => {
    if (!newEvent.title || !selectedDate) return;
    
    const event = {
      id: Date.now(),
      title: newEvent.title,
      time: newEvent.time,
      type: newEvent.type,
      date: selectedDate.toISOString().split('T')[0]
    };
    
    setEvents([...events, event]);
    setNewEvent({ title: "", time: "", type: "study" });
    setShowModal(false);
  };

  const deleteEvent = (eventId) => {
    setEvents(events.filter(e => e.id !== eventId));
  };

  const getEventTypeColor = (type) => {
    switch (type) {
      case "study": return "#652D90";
      case "exam": return "#DC2626";
      case "wellbeing": return "#059669";
      case "meeting": return "#2563EB";
      default: return "#652D90";
    }
  };

  const monthNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

  const days = getDaysInMonth(currentDate);
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <div className="calendar-title">
          <Calendar size={24} color="#652D90" />
          <h2>Calendrier</h2>
        </div>
        <div className="calendar-nav">
          <button onClick={prevMonth} className="nav-btn">
            <ChevronLeft size={20} />
          </button>
          <span className="current-month">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </span>
          <button onClick={nextMonth} className="nav-btn">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      <div className="calendar-grid">
        <div className="calendar-day-header">Dim</div>
        <div className="calendar-day-header">Lun</div>
        <div className="calendar-day-header">Mar</div>
        <div className="calendar-day-header">Mer</div>
        <div className="calendar-day-header">Jeu</div>
        <div className="calendar-day-header">Ven</div>
        <div className="calendar-day-header">Sam</div>

        {days.map((date, index) => {
          if (!date) return <div key={index} className="calendar-day empty" />;
          
          const dateStr = date.toISOString().split('T')[0];
          const dayEvents = getEventsForDate(date);
          const isToday = dateStr === today;
          const isSelected = selectedDate && dateStr === selectedDate.toISOString().split('T')[0];

          return (
            <div
              key={index}
              className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedDate(date)}
            >
              <span className="day-number">{date.getDate()}</span>
              {dayEvents.length > 0 && (
                <div className="event-indicators">
                  {dayEvents.slice(0, 3).map((event, i) => (
                    <div
                      key={i}
                      className="event-dot"
                      style={{ backgroundColor: getEventTypeColor(event.type) }}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedDate && (
        <div className="selected-date-panel">
          <div className="selected-date-header">
            <h3>
              {selectedDate.toLocaleDateString('fr-FR', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </h3>
            <button
              onClick={() => setShowModal(true)}
              className="add-event-btn"
              style={{ backgroundColor: "#652D90" }}
            >
              <Plus size={18} />
              Ajouter
            </button>
          </div>
          
          <div className="events-list">
            {getEventsForDate(selectedDate).length === 0 ? (
              <p className="no-events">Aucun événement ce jour</p>
            ) : (
              getEventsForDate(selectedDate).map(event => (
                <div key={event.id} className="event-item">
                  <div className="event-info">
                    <div className="event-time">
                      <Clock size={16} />
                      {event.time || "Toute la journée"}
                    </div>
                    <div className="event-title">{event.title}</div>
                  </div>
                  <button
                    onClick={() => deleteEvent(event.id)}
                    className="delete-event-btn"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Ajouter un événement</h3>
            <div className="form-group">
              <label>Titre</label>
              <input
                type="text"
                value={newEvent.title}
                onChange={e => setNewEvent({ ...newEvent, title: e.target.value })}
                placeholder="Ex: Examen de mathématiques"
              />
            </div>
            <div className="form-group">
              <label>Heure</label>
              <input
                type="time"
                value={newEvent.time}
                onChange={e => setNewEvent({ ...newEvent, time: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Type</label>
              <select
                value={newEvent.type}
                onChange={e => setNewEvent({ ...newEvent, type: e.target.value })}
              >
                <option value="study">Étude</option>
                <option value="exam">Examen</option>
                <option value="wellbeing">Bien-être</option>
                <option value="meeting">Réunion</option>
              </select>
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowModal(false)} className="cancel-btn">Annuler</button>
              <button onClick={addEvent} className="confirm-btn" style={{ backgroundColor: "#652D90" }}>
                Ajouter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
