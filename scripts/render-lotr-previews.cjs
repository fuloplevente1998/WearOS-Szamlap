// Design previews, NOT Wear OS screenshots. Source-of-truth: WFF XML and packed artwork.
// Chromium measures the actual drawn sample strings at Galaxy Watch7-scale sizes.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const drawable = path.join(root,'lotrwatchface/src/main/res/drawable-nodpi');
  const out = path.join(root,'dist/lotr-preview');
  fs.mkdirSync(out,{recursive:true});
  const xml = fs.readFileSync(path.join(root,'lotrwatchface/src/main/res/raw/watchface.xml'),'utf8');
  const names = ['lotr_middle_earth_map','lotr_one_ring_bezel','lotr_hour_hand','lotr_minute_hand','lotr_second_hand'];
  const assets = {};
  for (const name of names) {
    const file = path.join(drawable,name+'.png');
    if (!fs.existsSync(file)) throw new Error('Missing rasterized LOTR artwork: '+file);
    assets[name] = 'data:image/png;base64,'+fs.readFileSync(file).toString('base64');
  }
  const options = {headless:true};
  if (process.env.CHROMIUM_PATH) options.executablePath=process.env.CHROMIUM_PATH;
  const browser=await chromium.launch(options);
  try {
    const page=await browser.newPage({viewport:{width:480,height:480}});
    const results=await page.evaluate(async ({xml,assets}) => {
      const parsed=new DOMParser().parseFromString(xml,'application/xml');
      if(parsed.querySelector('parsererror'))throw new Error('Invalid WFF XML');
      const slots=[...parsed.querySelectorAll('ComplicationSlot')];
      if(slots.length!==5) throw new Error('Expected 5 native complication slots');
      const ordered=['lotr_battery_slot','lotr_heart_rate_slot','lotr_steps_slot','lotr_date_slot','lotr_workout_slot'];
      const samples=['100%','199 BPM','100 000','OCT 20','NYITÁS'];
      const images={};
      for(const [k,v] of Object.entries(assets)){
        const img=new Image();img.src=v;await img.decode();images[k]=img;
      }
      const output=[];
      const checks=[];
      const scene=parsed.querySelector('Scene');
      const sceneChecks=[];
      const previewTime=parsed.querySelector('Metadata[key="PREVIEW_TIME"]').getAttribute('value').split(':').map(Number);
      const [hour,minute,second]=previewTime;
      const angles={HourHand:((hour%12)+(minute+second/60)/60)*30,MinuteHand:(minute+second/60)*6,SecondHand:second*6};
      const testCanvas=document.createElement('canvas');
      const measure=testCanvas.getContext('2d');
      function number(el,attr){return Number(el.getAttribute(attr));}
      // WFF alpha is 0..255, unlike Canvas's 0..1. Only the current mode applies.
      function alpha(el,ambient){
        const variant=ambient?[...el.children].find(v=>v.tagName==='Variant'&&v.getAttribute('mode')==='AMBIENT'&&v.getAttribute('target')==='alpha'):null;
        const value=variant?Number(variant.getAttribute('value')):Number(el.getAttribute('alpha')??255);
        if(!Number.isInteger(value)||value<0||value>255)throw new Error('WFF alpha must be an integer in 0..255');
        return value/255;
      }
      for(const size of [432,480]){
        const scale=size/450;
        for(let i=0;i<slots.length;i++){
          const slot=slots[i];
          if(slot.getAttribute('displayName')!==ordered[i])throw new Error('Slot order changed');
          const comp=slot.querySelector('Complication[type="SHORT_TEXT"]')||slot.querySelector('Complication[type="LONG_TEXT"]');
          if(!comp)throw new Error('Missing short/long text renderer for slot '+i);
          const txt=[...comp.querySelectorAll('PartText')];
          if(txt.length!==2)throw new Error('Expected two text rows in '+ordered[i]);
          const top=txt[0],bottom=txt[1];
          const topEnd=number(top,'y')+number(top,'height');
          const bottomStart=number(bottom,'y');
          if(topEnd>bottomStart)throw new Error('Overlapping caption/value in '+ordered[i]);
          const title=top.querySelector('Font').textContent.trim();
          const x=number(slot,'x'),y=number(slot,'y'),w=number(slot,'width'),h=number(slot,'height');
          const corners=[[x,y],[x+w,y],[x,y+h],[x+w,y+h]];
          for(const [cx,cy] of corners)if(Math.hypot(cx-225,cy-225)>=190)
            throw new Error(ordered[i]+' encroaches on gold bezel');
          for(const [part,value] of [[top,title],[bottom,samples[i]]]){
            const font=part.querySelector('Font');
            const fontSize=number(font,'size');
            measure.font='700 '+(fontSize*scale)+'px sans-serif';
            const measured=measure.measureText(value).width;
            const available=(number(part,'width')-4)*scale;
            if(measured>available+0.01)throw new Error(ordered[i]+' text overflow ('+value+') at '+size+': '+measured.toFixed(1)+'px > '+available.toFixed(1)+'px');
            if(fontSize>number(part,'height')-2)throw new Error(ordered[i]+' vertical text clipping');
            checks.push({size,slot:ordered[i],row:part===top?'caption':'value',value,measuredWidthPx:+measured.toFixed(2),availableWidthPx:+available.toFixed(2),pass:true});
          }
        }
        for(const ambient of [false,true]){
          const canvas=document.createElement('canvas');canvas.width=size;canvas.height=size;
          const ctx=canvas.getContext('2d');
          ctx.fillStyle=scene.getAttribute('backgroundColor');ctx.fillRect(0,0,size,size);
          ctx.save();ctx.scale(scale,scale);
          ctx.beginPath();ctx.arc(225,225,225,0,Math.PI*2);ctx.clip();
          const drawn=[];
          // This is a limited illustration renderer, not a complete WFF runtime.
          // Walk the source scene order and reject unsupported new scene elements.
          for(const element of scene.children){
            const opacity=alpha(element,ambient);
            if(opacity===0)continue;
            ctx.save();ctx.globalAlpha=opacity;
            if(element.tagName==='PartImage'){
              const resource=element.querySelector('Image').getAttribute('resource');
              ctx.drawImage(images[resource],number(element,'x'),number(element,'y'),number(element,'width'),number(element,'height'));
              drawn.push({layer:resource,alpha:opacity});
            }else if(element.tagName==='ComplicationSlot'){
              const slot=element,i=slots.indexOf(slot);
              const x=number(slot,'x'),y=number(slot,'y'),w=number(slot,'width'),h=number(slot,'height');
              const p=(slot.querySelector('Complication[type="SHORT_TEXT"]')||slot.querySelector('Complication[type="LONG_TEXT"]'));
              const txt=[...p.querySelectorAll('PartText')];
              ctx.fillStyle='#CCB28A';ctx.fillRect(x,y,w,h);
              ctx.strokeStyle='#6E4927';ctx.lineWidth=1.1;ctx.strokeRect(x+.5,y+.5,w-1,h-1);
              ctx.strokeStyle='#E6C796';ctx.lineWidth=.55;ctx.strokeRect(x+3,y+3,w-6,h-6);
              txt.forEach((part,n)=>{
                const font=part.querySelector('Font');
                const text=n===0?font.textContent.trim():samples[i];
                const size=number(font,'size'), px=x+number(part,'x'),py=y+number(part,'y');
                ctx.font='700 '+size+'px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
                ctx.fillStyle='#342317';ctx.fillText(text,px+number(part,'width')/2,py+number(part,'height')/2);
              });
              drawn.push({layer:slot.getAttribute('displayName'),alpha:opacity});
            }else if(element.tagName==='AnalogClock'){
              for(const hand of element.children){
                const handAlpha=alpha(hand,ambient);
                if(handAlpha===0)continue;
                if(!(hand.tagName in angles))throw new Error('Unsupported clock child: '+hand.tagName);
                const w=number(hand,'width'),h=number(hand,'height'),px=number(hand,'pivotX'),py=number(hand,'pivotY');
                ctx.save();ctx.globalAlpha*=handAlpha;
                ctx.translate(number(element,'x')+number(hand,'x')+w*px,number(element,'y')+number(hand,'y')+h*py);
                ctx.rotate(angles[hand.tagName]*Math.PI/180);
                ctx.drawImage(images[hand.getAttribute('resource')],-w*px,-h*py,w,h);
                ctx.restore();drawn.push({layer:hand.tagName,alpha:opacity*handAlpha});
              }
            }else if(element.tagName==='PartDraw'){
              ctx.translate(number(element,'x'),number(element,'y'));
              for(const ellipse of element.children){
                if(ellipse.tagName!=='Ellipse')throw new Error('Unsupported hub primitive: '+ellipse.tagName);
                const w=number(ellipse,'width'),h=number(ellipse,'height');
                ctx.fillStyle=ellipse.querySelector('Fill').getAttribute('color');
                ctx.beginPath();ctx.ellipse(number(ellipse,'x')+w/2,number(ellipse,'y')+h/2,w/2,h/2,0,0,Math.PI*2);ctx.fill();
              }
              drawn.push({layer:'hub',alpha:opacity});
            }else throw new Error('Unsupported scene element: '+element.tagName);
            ctx.restore();
          }
          sceneChecks.push({size,mode:ambient?'ambient':'active',drawn});
          ctx.restore();
          output.push({filename:'one-ring-'+size+(ambient?'-ambient':'-active')+'.png',base64:canvas.toDataURL('image/png').split(',')[1]});
        }
      }
      return {output,checks,sceneChecks,note:'Raster previews with illustrative sample values; not Wear OS runtime capture.'};
    },{xml,assets});
    for(const item of results.output)fs.writeFileSync(path.join(out,item.filename),Buffer.from(item.base64,'base64'));
    // The Wear OS picker must display THIS revision, not the old mockup with static hands.
    // Preview-only samples are intentional; watch runtime values always come from providers.
    const picker = results.output.find(item => item.filename === 'one-ring-432-active.png');
    if (!picker) throw new Error('Missing generated watch-face picker preview');
    fs.writeFileSync(path.join(drawable,'lotr_preview.png'), Buffer.from(picker.base64,'base64'));
    fs.writeFileSync(path.join(out,'layout-report.json'),JSON.stringify({checks:results.checks,sceneChecks:results.sceneChecks,note:results.note},null,2)+'\n');
    console.log('PASS: 432/480 px sample text bounds and non-overlapping rows; '+results.output.length+' active/ambient previews generated');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
