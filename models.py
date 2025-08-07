from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date, timedelta

Base = declarative_base()

# ✅ Company Model
class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    gst_number = Column(String, nullable=True, default="")
    pan_number = Column(String, nullable=True, default="")
    logo_path = Column(String, nullable=True)        # path to logo image
    owner_signature_path = Column(String, nullable=True)  # path to owner's sign

    
    users = relationship('User', back_populates='company', cascade='all, delete-orphan')
    customers = relationship('Customer', back_populates='company', cascade='all, delete-orphan')
    service_items = relationship('ServiceItem', back_populates='company', cascade='all, delete-orphan')
    service_requests = relationship('ServiceRequest', back_populates='company', cascade='all, delete-orphan')
    service_catalogs = relationship('ServiceCatalog', back_populates='company', cascade='all, delete-orphan')



# ✅ User Model
class User(Base):
    __tablename__ = 'users'
    full_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    registration_date = Column(Date, default=date.today)
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
    phone = Column(String, nullable=True)
    address = Column(String)

    company = relationship('Company', back_populates='customers')
    requests = relationship('ServiceRequest', back_populates='customer', cascade='all, delete-orphan')

class ServiceCatalog(Base):
    __tablename__ = 'service_catalogs'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    category = Column(String, nullable=False)
    amc_years = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  # total price
    visits_per_year = Column(Integer, nullable=False)
    comprehensive_price = Column(Integer, default=False)  # ✅ Added field

    company = relationship('Company', back_populates='service_catalogs')

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
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created the request
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

    def generate_visits(self, session):
        for item in self.items:
            # Default to 1 if visits_per_year is None
            visits_per_year = item.visits_per_year or 1
            amc_years = item.amc_years or 1

            total_visits = visits_per_year * amc_years

            for i in range(total_visits):
                visit = Visit(
                    request_id=self.id,
                    service_item_id=item.id,    
                    scheduled_date=self.start_time + timedelta(days=i * 30),  # Example: every 30 days
                    completed=False,
                    visit_number=i + 1,
                )
                session.add(visit)

        session.commit()


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
    visits_per_year = Column(Integer)  

    request = relationship('ServiceRequest', back_populates='items')
    company = relationship('Company', back_populates='service_items')
    visits = relationship('Visit', back_populates='service_item', cascade="all, delete-orphan")
    
    def calculate_pricing(self, catalog: ServiceCatalog):
        self.base_price = catalog.price
        self.visits_per_year = catalog.visits_per_year  # ✅ store from catalog
        self.comprehensive_charge = catalog.comprehensive_price if self.comprehensive.lower() == 'yes' else 0
        self.total_price = (self.base_price + self.comprehensive_charge) * self.quantity


# ✅ Visit Model Update
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


