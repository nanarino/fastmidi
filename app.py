import os
from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from enum import Enum
import core
PORT = 8010


class Enum_repr_mixin:
    def __repr__(self):
        return repr(self.value)


class beat(Enum_repr_mixin, Enum):
    """拍"""
    nuden24 = '2,4'
    nuden44 = '4,4'
    def get_score(self) -> tuple[int, int]:
        numerator, denominator = self.value.split(',')
        return int(numerator), int(denominator)

class major(Enum_repr_mixin, Enum):
    """调"""
    C = 'C'
    Csp = 'C#'
    D = 'D'
    Dsp = 'D#'
    E = 'E'
    F = 'F'
    Fsp = 'F#'
    G = 'G'
    Gsp = 'G#'
    A = 'A'
    Asp = 'A#'
    B = 'B'


app = FastAPI(title='fastmidi api', description="""快速生成midi""")


@app.on_event("startup")
async def startup():
    os.system(f'start http://127.0.0.1:{PORT}')


@app.post('/midi',response_class=StreamingResponse)
async def post_midi(d: major = Form(...), n: beat = Form(...), bpm: int = Form(...), li: str = Form(...)):
    output_buffer = core.main(d.value, *n.get_score(), bpm, li)
    output_filename = 'output.mid'
    headers = {
        "content-type":'audio/mid',
        "content-disposition":f"attachment;filename={output_filename}"
    }
    return StreamingResponse(output_buffer,headers=headers)


app.mount("/", StaticFiles(directory=Path(__file__).parent.joinpath("static"), html=True))


if __name__ == '__main__':
    os.system('')
    import uvicorn
    uvicorn.run(app="app:app", host="0.0.0.0", port=PORT, reload=True, debug=True)
