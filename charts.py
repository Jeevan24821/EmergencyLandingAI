def bar_chart_html(zones):
    labels  = [z["name"] for z in zones]
    scores  = [z["score"] for z in zones]
    colors  = [
        "#00ff9d" if s > 80 else "#00d4ff" if s > 55 else "#ffb800" if s > 30 else "#ff3d71"
        for s in scores
    ]
    bg_colors = [c + "44" for c in colors]

    labels_js  = str(labels)
    scores_js  = str(scores)
    colors_js  = str(colors)
    bg_js      = str(bg_colors)

    return f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
  * {{ margin:0;padding:0;box-sizing:border-box }}
  body {{ background:#0f1527; padding:12px }}
  canvas {{ border-radius:8px }}
</style>
</head>
<body>
<div style="position:relative;width:100%;height:220px">
  <canvas id="bc"></canvas>
</div>
<script>
new Chart(document.getElementById('bc'),{{
  type:'bar',
  data:{{
    labels:{labels_js},
    datasets:[{{
      label:'Score',
      data:{scores_js},
      backgroundColor:{bg_js},
      borderColor:{colors_js},
      borderWidth:2,
      borderRadius:6,
      borderSkipped:false
    }}]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{display:false}},tooltip:{{
      backgroundColor:'#1a2240',
      borderColor:'rgba(0,212,255,0.3)',borderWidth:1,
      titleColor:'#00d4ff',bodyColor:'#c0c8e0',
      titleFont:{{family:'monospace',size:11}},
      bodyFont:{{family:'monospace',size:11}},
      callbacks:{{label:c=>' Score: '+c.parsed.y}}
    }}}},
    scales:{{
      x:{{grid:{{color:'rgba(0,212,255,0.05)'}},ticks:{{color:'#8892b0',font:{{family:'monospace',size:11}}}}}},
      y:{{grid:{{color:'rgba(0,212,255,0.05)'}},ticks:{{color:'#8892b0',font:{{family:'monospace',size:10}}}}}}
    }}
  }}
}});
</script>
</body>
</html>
"""


def radar_chart_html(zone, factor_scores):
    labels = list(factor_scores.keys())
    values = list(factor_scores.values())
    score  = zone["score"]
    col    = ("#00ff9d" if score > 80 else "#00d4ff" if score > 55
              else "#ffb800" if score > 30 else "#ff3d71")

    return f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
  * {{ margin:0;padding:0;box-sizing:border-box }}
  body {{ background:#0f1527; padding:12px }}
</style>
</head>
<body>
<div style="position:relative;width:100%;height:240px">
  <canvas id="rc"></canvas>
</div>
<script>
new Chart(document.getElementById('rc'),{{
  type:'radar',
  data:{{
    labels:{labels},
    datasets:[{{
      data:{values},
      backgroundColor:'{col}22',
      borderColor:'{col}',
      borderWidth:2,
      pointBackgroundColor:'{col}',
      pointRadius:4,
      pointHoverRadius:6
    }}]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{display:false}},tooltip:{{
      backgroundColor:'#1a2240',
      borderColor:'rgba(0,212,255,0.3)',borderWidth:1,
      titleColor:'#00d4ff',bodyColor:'#c0c8e0',
      titleFont:{{family:'monospace',size:11}},
      bodyFont:{{family:'monospace',size:11}}
    }}}},
    scales:{{r:{{
      backgroundColor:'rgba(10,14,26,0.7)',
      grid:{{color:'rgba(0,212,255,0.1)'}},
      pointLabels:{{color:'#8892b0',font:{{family:'monospace',size:10}}}},
      ticks:{{display:false,backdropColor:'transparent'}},
      angleLines:{{color:'rgba(0,212,255,0.08)'}},
      suggestedMin:0,suggestedMax:100
    }}}}
  }}
}});
</script>
</body>
</html>
"""


def gauge_html(score):
    col = ("#00ff9d" if score > 80 else "#00d4ff" if score > 55
           else "#ffb800" if score > 30 else "#ff3d71")
    label = ("SAFE" if score > 80 else "MODERATE" if score > 55
             else "CAUTION" if score > 30 else "DANGER")
    pct = max(0, min(100, (score + 20) / 150 * 100))
    deg = pct / 100 * 180

    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{margin:0;padding:0;box-sizing:border-box}}
  body {{background:#0f1527;display:flex;align-items:center;justify-content:center;padding:16px}}
  .gauge-wrap {{text-align:center;width:200px}}
  .gauge {{position:relative;width:180px;height:90px;overflow:hidden;margin:0 auto}}
  .gauge-bg {{width:180px;height:90px;border-radius:90px 90px 0 0;
              background:conic-gradient(from 180deg at 50% 100%,
                #ff3d71 0deg, #ffb800 45deg, #00d4ff 90deg, #00ff9d 135deg, #00ff9d 180deg);
              opacity:0.15}}
  .needle {{position:absolute;bottom:0;left:50%;width:3px;height:80px;
            background:{col};transform-origin:bottom center;
            transform:rotate({deg - 90}deg);border-radius:2px;
            box-shadow:0 0 8px {col}}}
  .hub {{position:absolute;bottom:-6px;left:50%;transform:translateX(-50%);
         width:14px;height:14px;border-radius:50%;background:{col};
         box-shadow:0 0 10px {col}}}
  .score-val {{font-size:28px;font-weight:700;color:{col};
               font-family:'Space Mono',monospace;margin-top:6px}}
  .score-lbl {{font-size:11px;color:#8892b0;font-family:'Space Mono',monospace;
               letter-spacing:0.12em;text-transform:uppercase;margin-top:2px}}
</style>
</head>
<body>
<div class="gauge-wrap">
  <div class="gauge">
    <div class="gauge-bg"></div>
    <div class="needle"></div>
    <div class="hub"></div>
  </div>
  <div class="score-val">{score}</div>
  <div class="score-lbl">{label}</div>
</div>
</body>
</html>
"""


def mini_bar_html(label, value, color="#00d4ff"):
    return f"""
<div style="margin-bottom:8px;font-family:'Space Mono',monospace">
  <div style="display:flex;justify-content:space-between;
              font-size:10px;color:#8892b0;margin-bottom:3px">
    <span>{label}</span><span style="color:{color}">{value}</span>
  </div>
  <div style="background:rgba(255,255,255,0.06);border-radius:3px;height:4px">
    <div style="width:{value}%;background:{color};height:100%;border-radius:3px"></div>
  </div>
</div>
"""
