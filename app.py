from init import init_app
import flask_excel as excel
from flask_bootstrap import Bootstrap


app = init_app()
Bootstrap(app)

if __name__ == "__main__":
    excel.init_excel(app)
    app.run(debug=False)
