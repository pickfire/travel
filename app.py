from sanic import Sanic
from sanic.log import log
from sanic.response import text, redirect
from sanic_jinja2 import SanicJinja2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model

from datetime import datetime, date

app = Sanic(__name__)
jinja = SanicJinja2(app)

@app.route('/')
async def get(req):
    user, tours, token = '', [], req.cookies.get('session', '')
    if token: # Check if session exist in cookie
        query = session.query(model.Session).filter_by(token=token)
        result = query.one_or_none()

        if not result or result.expiresAt < datetime.now(): # delete session if expired
            query.delete()
            req = jinja.render('index.html', req)
            del req.cookies['session']
            return req

        user = session.query(model.User).filter_by(id=result.userid).first()
        if str(user.role) == 'role.employee':
            tours = session.query(model.Tour).filter_by(employee_id=user.id).all()
        elif str(user.role) == 'role.manager':
            tours = session.query(model.Tour).filter_by(manager_id=user.id, state='submitted').all()
        elif str(user.role) == 'role.finance':
            tours = session.query(model.Tour).filter_by(finance_id=user.id, state='submitted').all()
        else:
            log.warn('none of the above')

    return jinja.render('index.html', req, user=user, tours=tours)

@app.route('/new', methods=['GET', 'POST'])
@app.route('/<id>', methods=['GET', 'POST'])
async def new(req, id=None):
    msg, token = '', req.cookies.get('session', '')
    if not token:
        redirect('/')

    query = session.query(model.Session).filter_by(token=token)
    result = query.first()
    if not result or result.expiresAt < datetime.now(): # delete session if expired
        query.delete()
        req = redirect('/')
        del req.cookies['session']
        return req

    user = session.query(model.User).filter_by(id=result.userid).one()
    tour = session.query(model.Tour).filter_by(id=id).one_or_none()
    s_mg = session.query(model.User).filter_by(id=tour.manager_id).one_or_none() if tour else ''
    s_mg = s_mg.name if s_mg else None

    if req.method == 'GET':
        pass
    elif str(user.role) == 'role.employee':
        forms = {
            'name': req.form.get('name'),
            'desc': req.form.get('desc', ''),
            'state': 'draft' if 'save' in req.form['state'] else 'submitted',
            'start': datetime.strptime(req.form.get('start', str(date.today())), '%Y-%m-%d'),
            'end': datetime.strptime(req.form.get('end', str(date.today())), '%Y-%m-%d'),
            'ticket_cost': req.form.get('ticket_cost', 0),
            'cab_home_cost': req.form.get('cab_home_cost', 0),
            'cab_dest_cost': req.form.get('cab_dest_cost', 0),
            'hotel_cost': req.form.get('hotel_cost', 0),
            'local_conveyance': req.form.get('local_conveyance', ''),
            'employee_id': user.id
        }

        if not tour:
            pass
        elif str(tour.state) == 'state.draft':
            q = session.query(model.User).filter_by(name=req.form.get('manager', '')).one_or_none()
            if q:
                forms['manager_id'] = q.id
        elif 'manager_id' in tour:
            forms['manager_id'] = tour.manager_id

        if tour:
            session.query(model.Tour).filter_by(id=id).update(forms)
        else:
            session.add(model.Tour(**forms))
        msg = "saved" if forms['state'] == "draft" else "submitted"

    elif str(user.role) == 'role.manager':
        session.query(model.Tour).filter_by(id=id).update({'state': req.form.get('state')})
    session.commit()

    mgs = [m.name for m in session.query(model.User).filter_by(role='manager').all()]
    return jinja.render('tour.html', req, user=user, tour=tour, message=msg, managers=mgs, the_man=s_mg)

@app.route('/login', methods=['GET', 'POST'])
async def login(req):
    if req.method == 'POST':
        res = redirect('/')
        if 'session' in req.cookies:
            return res

        query = session.query(model.User).filter_by(
                name=req.form.get('username', ''),
                pasw=req.form.get('password', '')).first()

        if query:
            ss = model.Session(userid=query.id)
            session.add(ss)
            session.commit()
            res.cookies['session'] = ss.token
            return res
        else:
            return jinja.render('login.html', req, message="Invalid password!")
    else:
        return jinja.render('login.html', req)

engine = create_engine('sqlite:///:memory:')
model.Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

u1 = model.User(name='name', pasw='pass', role='employee')
s1 = model.Tour(name='Post', employee_id=1)
u2 = model.User(name='mann', pasw='pass', role='manager')
s2 = model.Tour(name='<script>alert("hello");</script>', employee_id=1, manager_id=2, state='submitted')
session.add_all([u1, s1, u2, s2])
session.commit()

if __name__ == '__main__':
    app.run(debug=True)
