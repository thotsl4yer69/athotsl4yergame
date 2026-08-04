(() => {
  'use strict';
  const c = document.getElementById('game');
  const x = c.getContext('2d');
  x.imageSmoothingEnabled = false;
  const W = 480, H = 320, FLOOR = 257;
  const screenshotMode = new URLSearchParams(location.search).has('screenshot');
  const demoMode = screenshotMode || new URLSearchParams(location.search).has('demo');

  const state = {
    time: screenshotMode ? 18.35 : 0,
    last: performance.now(),
    shake: 0,
    flash: 0,
    score: 131269,
    combo: 6,
    vibe: 79,
    hp: 83,
    bossHp: 64,
    player: { px: 135, py: FLOOR, vx: 0, vy: 0, face: 1, attack: 0.43, kick: 0, hit: 0, special: 0 },
    siren: { px: 310, py: FLOOR, phase: 1.2, hit: 0.18, attack: 0, face: -1 },
    vandal: { px: 405, py: FLOOR + 6, phase: 2.8, hit: 0, attack: 0.6, face: -1 },
    pidge: { px: 227, py: 198, wing: 0 },
    pickups: [
      { kind: 'KRN', px: 252, py: 241, bob: 1.3 },
      { kind: 'DUST', px: 367, py: 243, bob: 2.6 },
    ],
    keys: new Set(),
    message: 'PIDGE: THE WHITE PACKET IS PROBABLY A POWER-UP.',
  };

  const C = {
    ink: '#080510', black: '#030208', white: '#fff8ed', cream: '#ffd8b4', skin: '#d98c70', skinHi: '#f2b38e',
    magenta: '#ff2c9f', pink: '#ff6bc1', cyan: '#25e6dd', blue: '#3a74ff', purple: '#8e39d8', violet: '#4b1a82',
    gold: '#ffcf3f', orange: '#ff7b27', red: '#ee244f', green: '#63e37d', gray: '#8c8998', dark: '#171023',
  };

  function rect(px, py, w, h, fill, stroke = null) {
    x.fillStyle = fill; x.fillRect(Math.round(px), Math.round(py), Math.round(w), Math.round(h));
    if (stroke) { x.strokeStyle = stroke; x.lineWidth = 1; x.strokeRect(Math.round(px)+.5, Math.round(py)+.5, Math.round(w)-1, Math.round(h)-1); }
  }
  function poly(points, fill, stroke = null) {
    x.beginPath(); x.moveTo(points[0][0], points[0][1]);
    for (let i=1;i<points.length;i++) x.lineTo(points[i][0],points[i][1]);
    x.closePath(); x.fillStyle=fill; x.fill(); if(stroke){x.strokeStyle=stroke;x.lineWidth=1;x.stroke();}
  }
  function ell(px,py,rx,ry,fill,stroke=null){x.beginPath();x.ellipse(px,py,rx,ry,0,0,Math.PI*2);x.fillStyle=fill;x.fill();if(stroke){x.strokeStyle=stroke;x.lineWidth=1;x.stroke();}}
  function line(ax,ay,bx,by,color,width=1){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(ax,ay);x.lineTo(bx,by);x.stroke();}
  function text(s, px, py, size=8, color=C.white, align='left', shadow=true) {
    x.font = `bold ${size}px ui-monospace, monospace`; x.textAlign=align; x.textBaseline='top';
    if(shadow){x.fillStyle='#000';x.fillText(s,px+1,py+1);} x.fillStyle=color;x.fillText(s,px,py);
  }

  function background(t) {
    const g = x.createLinearGradient(0,0,0,220); g.addColorStop(0,'#080317');g.addColorStop(.5,'#1b0731');g.addColorStop(1,'#3e0f3d');
    x.fillStyle=g;x.fillRect(0,0,W,H);
    for(let i=0;i<9;i++){
      const bx=i*58-((t*5)%58); const bh=52+(i%4)*13;
      rect(bx,88-bh,47,bh,'#0a0b20','#40185e');
      for(let wy=45;wy<82;wy+=10) for(let wx=bx+5;wx<bx+42;wx+=10) if(((i+wx+wy)|0)%3) rect(wx,wy,3,4,'#623c8f');
    }
    rect(154,15,172,29,'#12061f','#fc2ba1'); rect(158,19,164,21,'#270b35','#57eee4');
    text('TH0TSL4YER69',240,20,14,C.magenta,'center'); text('MAIN FLOOR MELTDOWN',240,37,5,C.cyan,'center',false);
    x.globalAlpha=.16;
    poly([[48,0],[152,205],[100,205]],C.cyan); poly([[430,0],[303,205],[362,205]],C.magenta); poly([[250,0],[215,205],[280,205]],C.gold);
    x.globalAlpha=1;
    rect(0,105,480,75,'#160b24','#5b216e'); rect(0,172,480,17,'#090611');
    for(let i=0;i<12;i++){const bx=8+i*40;rect(bx,122,19,42,'#29143c','#71338b');rect(bx+4,130,4,22,i%3===0?C.gold:i%3===1?C.cyan:C.magenta);rect(bx+11,136,4,16,C.pink);}
    rect(0,164,480,7,'#651560'); line(0,165,480,165,C.magenta,2);
    drawPoleStage(74,165,t,0); drawPoleStage(390,165,t,1);
    for(let i=0;i<24;i++){
      const cx=(i*23 + (i%3)*7)%500-10; const cy=184+(i%4)*3; const bob=Math.sin(t*3+i)*2;
      ell(cx,cy+bob,5,6,i%2?'#160f24':'#0e0a17'); rect(cx-5,cy+5+bob,10,24,i%3?'#120b1d':'#1d0c24');
      if(i%5===0) rect(cx+4,cy+8+bob,2,7,C.magenta);
    }
    rect(0,190,W,130,'#130d1b');
    for(let yy=190;yy<320;yy+=13) line(0,yy,W,yy,yy%26===8?'#3b1549':'#25132f',1);
    for(let xx=-80;xx<560;xx+=32) line(240,190,xx,320,'#32133c',1);
    line(0,FLOOR,W,FLOOR,'#ff2c9f',2); line(0,FLOOR+3,W,FLOOR+3,'#2be5df',1);
    rect(10,211,78,32,'#210f2f','#7c2e7d');rect(14,216,70,5,'#5d1c60');
    ell(37,211,10,4,'#33163f'); rect(35,195,4,16,C.gold); ell(37,194,3,5,C.gold);
    line(342,229,457,229,C.gold,2); rect(340,225,5,25,C.gold); rect(454,225,5,25,C.gold);
  }

  function drawPoleStage(cx, base, t, variant){
    const poleX=cx; line(poleX,70,poleX,base,'#d9d1e2',2); line(poleX+2,70,poleX+2,base,'#6e6577',1);
    ell(cx,base+2,30,8,'#281034','#a83389');
    x.save(); x.translate(cx,base-45); const s=variant?1:-1; const sway=Math.sin(t*1.6+variant)*3;
    ell(sway,-27,6,7,'#a13988');
    poly([[sway-8,-20],[sway+7,-20],[sway+11,4],[sway+6,20],[sway-9,20],[sway-12,3]],'#8b247a');
    ell(sway,4,10,12,'#a62a91');
    line(sway-8,-16,-s*13,-1,'#b13b9b',4);line(sway+8,-16,s*18,-7,'#b13b9b',4);
    line(sway-5,17,-s*10,39,'#8e277b',5);line(sway+5,17,s*13,40,'#8e277b',5);
    line(sway+8,-16,poleX-cx,8,'#e7b8dc',2);
    x.restore();
    text('LIVE',cx,75,5,variant?C.cyan:C.magenta,'center');
  }

  function drawPlayer(p,t){
    x.save(); x.translate(p.px,p.py); x.scale(p.face,1);
    const jump=-Math.max(0,Math.sin(Math.min(1,Math.abs(p.vy)/260)*Math.PI))*3;
    x.translate(0,jump);
    x.save();x.scale(p.face,1);ell(0,2,19,5,'#07040bbb');x.restore();
    poly([[-11,-35],[-3,-36],[-1,-8],[-9,-8]],'#15151e',C.cyan); poly([[3,-36],[11,-34],[13,-7],[4,-7]],'#15151e',C.cyan);
    rect(-12,-10,11,7,'#0c0b12'); rect(3,-9,13,7,'#0c0b12');
    poly([[-16,-69],[-3,-67],[-7,-30],[-19,-23]],'#174c61','#25e6dd'); poly([[5,-66],[17,-63],[20,-26],[8,-34]],'#174c61','#25e6dd');
    poly([[-13,-70],[10,-70],[16,-47],[10,-31],[-9,-31],[-16,-48]],'#21c7c5','#062e37');
    rect(-10,-61,18,9,'#f3cc47','#251821'); rect(-4,-52,7,20,'#11121b');
    if(p.attack>0){
      const ext=18+Math.sin(p.attack*Math.PI)*10;
      line(8,-61,ext,-53,C.skinHi,6); rect(ext-2,-57,17,7,C.gold,'#4b2509');
      poly([[ext+13,-60],[ext+30,-54],[ext+13,-48]],C.cyan);
      x.globalAlpha=.65; for(let i=0;i<4;i++) line(ext+13+i*7,-65-i,ext+28+i*8,-54,C.gold,2); x.globalAlpha=1;
    } else {line(9,-62,17,-45,C.skinHi,6);rect(13,-48,7,5,C.gold);}
    line(-10,-62,-17,-43,C.skinHi,6); rect(-20,-45,7,5,C.gold);
    ell(-1,-83,10,11,C.skinHi,'#4a241f');
    poly([[-11,-90],[-3,-99],[9,-94],[11,-83],[4,-91],[-9,-80]],'#101a2d','#2ee6e0');
    rect(2,-84,5,2,C.black); rect(5,-84,1,1,C.white); line(-1,-76,5,-76,C.red,1);
    rect(-1,-89,10,3,'#241031','#ff2c9f');
    text('69',-2,-60,6,C.black,'center',false);
    x.restore();
  }

  function drawSiren(e,t){
    x.save();x.translate(e.px,e.py);x.scale(e.face,1);
    const sway=Math.sin(t*3+e.phase)*2; x.translate(0,sway);
    ell(0,3,21,5,'#07040bbb');
    poly([[-13,-38],[-4,-39],[-2,-6],[-12,-6]],'#2b0b31',C.magenta);poly([[4,-39],[13,-37],[15,-6],[5,-6]],'#2b0b31',C.magenta);
    rect(-14,-9,13,6,'#110617');rect(4,-9,14,6,'#110617');
    poly([[-19,-73],[-10,-68],[-15,-25],[-25,-16]],'#5c134f','#ff57ba'); poly([[11,-69],[20,-66],[25,-18],[13,-27]],'#5c134f','#ff57ba');
    ell(0,-42,16,15,'#ec2e9b','#66103f');
    poly([[-13,-70],[13,-70],[17,-48],[11,-31],[-11,-31],[-17,-48]],'#f0359f','#651048');
    poly([[-11,-66],[0,-58],[11,-66],[8,-46],[0,-37],[-8,-46]],'#4d1b79','#ff8bd1');
    line(-8,-49,8,-49,C.gold,2);
    line(-11,-63,-21,-46,C.skinHi,6);line(11,-63,18,-49,C.skinHi,6);
    x.strokeStyle=C.white;x.lineWidth=3;x.beginPath();x.arc(25,-52,10,0,Math.PI*2);x.stroke();rect(22,-56,6,9,'#1b0e25','#72f6ec');
    ell(0,-83,10,11,C.skinHi,'#54243b');
    poly([[-10,-91],[-2,-99],[10,-94],[13,-84],[8,-76],[-11,-79]],'#4b0a4a','#ff2c9f');
    poly([[7,-92],[22,-96],[31,-85],[25,-75],[13,-78]],'#7b0b65','#ff54bb');
    rect(-5,-86,4,2,C.black);rect(3,-86,4,2,C.black);line(-4,-77,5,-77,'#c31555',2);
    if(e.hit>0){x.globalAlpha=.8;text('THOT BREAK!',0,-112,8,C.gold,'center');x.globalAlpha=1;}
    x.restore();
  }

  function drawVandal(e,t){
    x.save();x.translate(e.px,e.py);x.scale(e.face,1);const bob=Math.sin(t*4+e.phase)*2;x.translate(0,bob);
    ell(0,3,18,5,'#07040bbb');
    poly([[-12,-35],[-4,-36],[-2,-5],[-12,-5]],'#210c20',C.red);poly([[4,-36],[12,-34],[13,-5],[4,-5]],'#210c20',C.red);
    rect(-14,-8,13,6,'#080409');rect(3,-8,14,6,'#080409');
    poly([[-18,-67],[-9,-75],[1,-70],[13,-74],[19,-64],[12,-54],[-12,-54]],'#73284e','#ff6da9');
    ell(0,-42,14,14,'#8a154b','#e94f8a');
    poly([[-11,-62],[11,-62],[14,-43],[8,-29],[-8,-29],[-14,-43]],'#7a163f','#ff3c78');
    line(-8,-51,8,-51,C.black,2);line(0,-61,0,-31,C.gold,1);
    line(10,-57,20,-43,C.skinHi,5);x.strokeStyle=C.magenta;x.lineWidth=2;x.beginPath();x.arc(29,-44,15,0,Math.PI*1.75);x.stroke();
    line(-10,-58,-17,-42,C.skinHi,5);
    ell(0,-76,9,10,C.skinHi,'#4b202b');
    poly([[-10,-84],[-4,-92],[10,-87],[8,-73],[-9,-71]],'#130f18','#d73c7e');
    rect(-5,-79,4,2,C.black);rect(3,-79,4,2,C.black);line(-3,-70,5,-70,C.red,1);
    x.restore();
  }

  function drawPidge(p,t){
    x.save();x.translate(p.px,p.py+Math.sin(t*6)*3);x.scale(1.2,1.2);
    ell(0,0,9,6,'#707988','#1b1e28');ell(7,-3,5,5,'#89919c','#1b1e28');
    poly([[-7,-1],[-14,-6],[-11,3]],'#545d6b');poly([[11,-3],[17,-1],[11,1]],C.gold);
    rect(-2,-6,6,2,C.cyan);rect(7,-5,2,2,C.red);line(-2,5,-4,9,C.gold,1);line(3,5,4,9,C.gold,1);
    x.restore();
  }

  function drawPickup(it,t){
    const bob=Math.sin(t*4+it.bob)*3; x.save();x.translate(it.px,it.py+bob);
    if(it.kind==='KRN'){
      rect(-6,-16,12,17,C.gold,'#6f4d08');rect(-4,-13,8,3,C.white);rect(-4,-8,8,5,'#c59020');text('K',0,-12,5,C.black,'center',false);
    } else {
      poly([[-8,-11],[8,-11],[6,5],[-7,5]],C.white,'#7c7a88');rect(-6,-8,12,3,C.cyan);text('69',0,-5,5,C.violet,'center',false);
      x.globalAlpha=.45;ell(0,-4,13,11,C.white);x.globalAlpha=1;
    }
    x.restore();
  }

  function hud(t){
    rect(0,0,W,13,'#07040d');
    text('PLAYER // COOKED COURIER',12,6,6,C.cyan);text('NEON SIREN // LV.03',468,6,6,C.magenta,'right');
    rect(12,17,190,12,'#160b20','#b5589e');rect(15,20,184,6,'#431438');rect(15,20,Math.round(184*state.hp/100),6,C.cyan);
    rect(278,17,190,12,'#160b20','#b5589e');rect(281,20,184,6,'#431438');rect(465-Math.round(184*state.bossHp/100),20,Math.round(184*state.bossHp/100),6,C.magenta);
    poly([[230,13],[250,13],[258,29],[250,44],[230,44],[222,29]],'#2a1038','#ffcf3f');text('69',240,22,11,C.gold,'center');
    text(`SCORE ${state.score.toString().padStart(7,'0')}`,12,32,7,C.white);text(`VIBE ${state.vibe}%`,468,32,7,C.white,'right');
    rect(14,52,70,26,'#120818','#ff2c9f');text(`${state.combo} HIT`,49,55,12,C.gold,'center');text('THOT BREAK COMBO',49,69,5,C.white,'center');
    rect(395,51,72,29,'#100818','#25e6dd');text('PACKETS',431,54,6,C.cyan,'center');rect(404,64,9,9,C.gold);rect(420,64,9,9,C.white);rect(436,64,9,9,'#333');text('x2',457,65,7,C.white,'right');
    text('DISTRICT 1-3  //  MAIN FLOOR MELTDOWN',240,85,7,'#ffb6df','center');
  }

  function fx(t){
    if(state.player.attack>0){
      x.save();x.globalCompositeOperation='lighter';
      for(let i=0;i<10;i++){const a=i*0.79+t*4;const rr=15+(i%4)*4;line(220+Math.cos(a)*rr,205+Math.sin(a)*rr,220+Math.cos(a)*rr*1.6,205+Math.sin(a)*rr*1.6,i%2?C.cyan:C.gold,2);}
      ell(220,205,7+Math.sin(t*8)*2,7,C.white);x.restore();
    }
    for(let i=0;i<13;i++){const px=(i*47+t*28)%540-30;const py=235+(i%4)*16;rect(px,py,2+(i%3),1,i%2?C.magenta:C.cyan);}
    x.globalAlpha=.10; for(let yy=0;yy<H;yy+=3) rect(0,yy,W,1,'#000'); x.globalAlpha=1;
    const vg=x.createRadialGradient(W/2,H/2,100,W/2,H/2,300);vg.addColorStop(.5,'#0000');vg.addColorStop(1,'#000b');x.fillStyle=vg;x.fillRect(0,0,W,H);
    rect(40,283,400,27,'#08050f','#ff2c9f');rect(43,286,394,21,'#140b1e','#25e6dd');
    text(state.message,240,291,7,C.white,'center');
    text('TOUCH: LEFT / RIGHT / JUMP / ATTACK     KEYBOARD: ← → Z X',240,312,5,'#c9b5d2','center',false);
  }

  function update(dt){
    const p=state.player; const keys=state.keys;
    const accel=310;
    if(keys.has('ArrowLeft')||keys.has('a')){p.vx-=accel*dt;p.face=-1;}
    if(keys.has('ArrowRight')||keys.has('d')){p.vx+=accel*dt;p.face=1;}
    p.vx*=Math.pow(.05,dt);p.px=Math.max(60,Math.min(420,p.px+p.vx*dt));
    if((keys.has('z')||keys.has(' '))&&p.py>=FLOOR){p.vy=-210;}
    p.vy+=520*dt;p.py+=p.vy*dt;if(p.py>FLOOR){p.py=FLOOR;p.vy=0;}
    if(keys.has('x'))p.attack=Math.min(1,p.attack+dt*5);else p.attack=Math.max(0,p.attack-dt*2.2);
    if(demoMode){
      p.px=135+Math.sin(state.time*.7)*5;p.py=FLOOR;p.face=1;p.attack=.35+.25*Math.sin(state.time*4);
      state.siren.px=310+Math.sin(state.time*.8)*4;state.siren.hit=.3;
      state.vandal.px=405+Math.sin(state.time)*3;state.pidge.px=226+Math.sin(state.time*2)*8;
    }
  }

  function render(){
    x.save();
    if(state.shake>0)x.translate((Math.random()-.5)*state.shake,(Math.random()-.5)*state.shake);
    background(state.time);hud(state.time);
    state.pickups.forEach(p=>drawPickup(p,state.time));
    drawPidge(state.pidge,state.time);drawPlayer(state.player,state.time);drawSiren(state.siren,state.time);drawVandal(state.vandal,state.time);fx(state.time);
    x.restore();
  }

  function loop(now){
    const dt=Math.min(.034,(now-state.last)/1000||0);state.last=now;if(!screenshotMode)state.time+=dt;update(dt);render();requestAnimationFrame(loop);
  }
  addEventListener('keydown',e=>{state.keys.add(e.key);if(['ArrowLeft','ArrowRight',' ','z','x'].includes(e.key))e.preventDefault();});
  addEventListener('keyup',e=>state.keys.delete(e.key));
  let touchStart=null;
  c.addEventListener('pointerdown',e=>{touchStart={x:e.offsetX,y:e.offsetY,t:performance.now()};c.setPointerCapture(e.pointerId);});
  c.addEventListener('pointerup',e=>{
    if(!touchStart)return;const dx=e.offsetX-touchStart.x,dy=e.offsetY-touchStart.y;
    if(Math.abs(dy)>35){if(dy<0)state.player.vy=-220;else state.player.special=1;}
    else if(e.offsetX<W*.25)state.player.vx=-180;else if(e.offsetX<W*.5)state.player.vx=180;else if(e.offsetX<W*.75)state.player.vy=-220;else state.player.attack=1;
    touchStart=null;
  });
  requestAnimationFrame(loop);
})();
