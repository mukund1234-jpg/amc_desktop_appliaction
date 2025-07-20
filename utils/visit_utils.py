from models import ServiceRequest, Visit

def regenerate_visits_for_request(session, request_id):
    request = session.query(ServiceRequest).get(request_id)
    if request:
        session.query(Visit).filter_by(request_id=request_id).delete()
        session.commit()

        request.generate_visits(session=session)
        session.commit()
        print(f"Regenerated visits for request id {request_id}")
    else:
        print("Service request not found")
