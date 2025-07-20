from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date, timedelta

Base = declarative_base()

# ✅ Company Model
class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship('User', back_populates='company', cascade='all, delete-orphan')
    customers = relationship('Customer', back_populates='company', cascade='all, delete-orphan')
    service_items = relationship('ServiceItem', back_populates='company', cascade='all, delete-orphan')
    service_requests = relationship('ServiceRequest', back_populates='company', cascade='all, delete-orphan')


# ✅ User Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'office_worker'
    company_id = Column(Integer, ForeignKey('companies.id'))

    company = relationship('Company', back_populates='users')


# ✅ Customer Model
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)

    company = relationship('Company', back_populates='customers')
    requests = relationship('ServiceRequest', back_populates='customer', cascade='all, delete-orphan')


# ✅ ServiceRequest Model
class ServiceRequest(Base):
    __tablename__ = 'service_requests'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    status = Column(String, default='Pending')
    bill_file = Column(String, nullable=True)
    start_time = Column(Date)
    end_time = Column(Date)

    customer = relationship('Customer', back_populates='requests')
    company = relationship('Company', back_populates='service_requests')
    items = relationship('ServiceItem', back_populates='request', cascade="all, delete-orphan")
    visits = relationship('Visit', back_populates='request', cascade="all, delete-orphan")

    def complete_request(self, session=None):
        self.start_time = date.today()
        max_amc_years = max(item.amc_years for item in self.items)
        self.end_time = self.start_time + timedelta(days=365 * max_amc_years)
        self.status = 'Completed'
        self.generate_visits(session=session)

    def generate_visits(self, session=None):
        if not self.start_time:
            self.start_time = date.today()

        if session:
            session.query(Visit).filter_by(request_id=self.id).delete()

        for item in self.items:
            num_visits = 3 if item.amc_years == 1 else 9
            interval_days = 120
            for i in range(num_visits):
                visit_date = self.start_time + timedelta(days=i * interval_days)
                visit = Visit(
                    request_id=self.id,
                    service_item_id=item.id,
                    visit_number=i + 1,
                    scheduled_date=visit_date,
                    completed=False
                )
                if session:
                    session.add(visit)
                else:
                    self.visits.append(visit)


# ✅ ServiceItem Model
class ServiceItem(Base):
    __tablename__ = 'service_items'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('service_requests.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))

    category = Column(String)
    brand = Column(String)
    type = Column(String)
    quantity = Column(Integer)
    amc_years = Column(Integer)
    comprehensive = Column(String)
    base_price = Column(Integer)
    comprehensive_charge = Column(Integer)
    total_price = Column(Integer)

    request = relationship('ServiceRequest', back_populates='items')
    company = relationship('Company', back_populates='service_items')
    visits = relationship('Visit', back_populates='service_item', cascade="all, delete-orphan")

    def calculate_pricing(self):
        self.base_price = 1000 if self.amc_years == 1 else 3000
        self.comprehensive_charge = 300 if self.comprehensive.lower() == 'yes' else 0
        self.total_price = (self.base_price + self.comprehensive_charge) * self.quantity


# ✅ Visit Model
class Visit(Base):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('service_requests.id'))
    service_item_id = Column(Integer, ForeignKey('service_items.id'))
    visit_number = Column(Integer)
    scheduled_date = Column(Date)
    completed = Column(Boolean, default=False)

    request = relationship('ServiceRequest', back_populates='visits')
    service_item = relationship('ServiceItem', back_populates='visits')
