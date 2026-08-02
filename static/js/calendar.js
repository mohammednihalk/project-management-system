document.addEventListener('DOMContentLoaded', function () {

    var calendarEl = document.getElementById('calendar');

    // ===== ACTION MODAL =====
    const actionModal = document.getElementById('actionModal');
    const updateBtn = document.getElementById('updateEvent');
    const deleteBtn = document.getElementById('deleteEventBtn');
    const closeAction = document.getElementById('closeActionModal');

    let selectedEvent = null;

    // ===== ADD MODAL =====
    const modal = document.getElementById('eventModal');
    const openBtn = document.querySelector('.add-btn');
    const closeBtn = document.getElementById('closeModal');
    const saveBtn = document.getElementById('saveEvent');

    // ===== INIT CALENDAR =====
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: false,

        selectable: true,
        editable: true,

        events: eventsData,

        // ✅ ONLY ONE EVENT CLICK (EDIT MODAL)
        eventClick: function(info) {

            selectedEvent = info.event;

            document.getElementById('editTitle').value = info.event.title;
            document.getElementById('editDate').value = info.event.startStr;

            actionModal.style.display = "flex";
        },

        datesSet: function () {
            document.getElementById('calendarTitle').innerText =
                calendar.view.title;
        }
    });

    calendar.render();

    // ===== UPDATE EVENT =====
    updateBtn.addEventListener('click', () => {

        let newTitle = document.getElementById('editTitle').value;
        let newDate = document.getElementById('editDate').value;

        if (!newTitle || !newDate) {
            alert("Fill all fields");
            return;
        }

        fetch('/update-event/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: selectedEvent.id,
                title: newTitle,
                date: newDate
            })
        })
        .then(res => res.json())
        .then(data => {

            if (data.status === "updated") {
                selectedEvent.setProp('title', newTitle);
                selectedEvent.setStart(newDate);
            }

            actionModal.style.display = "none";
        });

    });

    // ===== DELETE EVENT =====
    deleteBtn.addEventListener('click', () => {

        fetch('/delete-event/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: selectedEvent.id })
        })
        .then(res => res.json())
        .then(data => {

            if (data.status === "deleted") {
                selectedEvent.remove();
            }

            actionModal.style.display = "none";
        });

    });

    // CLOSE EDIT MODAL
    closeAction.addEventListener('click', () => {
        actionModal.style.display = "none";
    });

    // ===== NAV BUTTONS =====
    document.getElementById('prevBtn').onclick = () => calendar.prev();
    document.getElementById('nextBtn').onclick = () => calendar.next();
    document.getElementById('todayBtn').onclick = () => calendar.today();

    // ===== VIEW BUTTONS =====
    const monthBtn = document.querySelector('.month-btn');
    const yearBtn = document.querySelector('.year-btn');

    function setActive(btn) {
        monthBtn.classList.remove('active-view');
        yearBtn.classList.remove('active-view');
        btn.classList.add('active-view');
    }

    monthBtn.addEventListener('click', () => {
        calendar.changeView('dayGridMonth');
        setActive(monthBtn);
    });

    yearBtn.addEventListener('click', () => {
        calendar.changeView('multiMonthYear');
        setActive(yearBtn);
    });

    setActive(monthBtn);

    // ===== ADD EVENT MODAL =====
    openBtn.addEventListener('click', () => {
        modal.style.display = "flex";
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = "none";
    });

    saveBtn.addEventListener('click', () => {

        let title = document.getElementById('eventTitle').value;
        let date = document.getElementById('eventDate').value;

        if (!title || !date) {
            alert("Fill all fields");
            return;
        }

        fetch('/add-event/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, date })
        })
        .then(res => res.json())
        .then(data => {

            calendar.addEvent({
                id: data.id,
                title: title,
                start: date,
                className: 'blue'
            });

            modal.style.display = "none";

            document.getElementById('eventTitle').value = "";
            document.getElementById('eventDate').value = "";
        });

    });

});