
## LinkedIn Job Filter (ATS Score)
This repo includes a lightweight script to **filter job listings by an ATS-style keyword score** and only apply to jobs **above a threshold (default: 80)**. The script expects a resume **text file** and a **JSON export** of job listings (from a compliant source).

### Files
`linkedin_job_bot.py`: main script.
`sample_jobs.json`: sample job listing data.

### Usage

1. Create a resume text file (plain `.txt`) with the content of your resume.
2. Run the script once or on an interval.

Run once:
```
python3 linkedin_job_bot.py \
  --jobs-file sample_jobs.json \
  --resume resume.txt \
  --threshold 80 \
  --once
```

Run on a schedule (minutes):
```
python3 linkedin_job_bot.py \
  --jobs-file sample_jobs.json \
  --resume resume.txt \
  --threshold 80 \
  --interval-minutes 15
```

Applications are logged to `applications.log`.
 
EOF
)
