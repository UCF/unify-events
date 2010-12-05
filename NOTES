-Unify-

Events/Calendar system to replace the UNL events and PHP/PEAR beast.

So giving props where props are due, the UNL events system is useful and is 
currently serving our needs at UCF.  I simply see opportunity to turn a hulking
and unwieldy beast of a web app into something a little less hulking and
unwieldy.

The UNL events code is difficult to extend and improve.  Surprisingly the system
itself runs relatively well, but making changes for bug fixes or feature changes
is tedious at best and impossible at worst without reworking entire
subcomponents.

--Goals--

The unify system should provide similar functionality to what UNL currently
provides as well as be easy to maintain.  This does not mean that I aim to
duplicate the UNL events system.  There are some processes I think can be
improved or removed altogether.  So goals:

* Improve maintainability and extendability
* Improve functionality where applicable
* Underlying the UNL events system, provide an easy to use and dependable events
repository for institutions of any size.

--Features--

* Full fledged user management.  I find users in UNL events to be second class
citizens, and this has caused some headaches in our workflow.
* Simple but effective events creation and management.
* Multiple Calendars
* Sharing of events between calendars
* Full usage of the django admin for management of calendars, users, and events

--System Objects--

---Users---

* Users should have the ability to create their own calendars.  Ideally they
can create as many calendars as they like.
* Users should be able to manage who has access to modify their calendars.
* Users cannot be removed from calendars they created.
* The above implies users may have access to many calendars, including calendars
they did not create.

---Calendars---

* A calendar has a creating user who is the admin for that calendar.
* Calendars have events that belong to them.
* A calendar can subscribe to other calendars, which means it displays events
from designated calendars on it's public page.  These events are not editable
from the calendar that is subscribing.
* Locations can be reused per calendar.  They will be pulled from events that
are currently part of the calendar. The site administrator will also be able
define a set of pre-determine locations to encourage uniform location values
when applicable.

---Events---

* An event can be recurring.
* An event can have multiple dates.
* An event can only belong to a single calendar
* Events can be suggested to/imported from other calendars.
* When an imported event's original is edited, the copied events' calendar owners are notified.
* Events may have images associated with them.


