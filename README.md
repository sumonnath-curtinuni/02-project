# AssessmentFlow CLI

**Unit:** ISYS5002 Introduction to Programming  
**Project:** Personal Assessment Sprint Planner  
**Language:** Python 3  
**Version:** 1.0.0

## Rationale

AssessmentFlow is a command-line program designed for a postgraduate student who regularly has several assessments active at the same time. A normal calendar tells me *when* work is due, but it does not directly answer a more practical question: **what should I study first today?** I wanted a small tool that combines due dates, assessment weight, my current progress and an estimate of remaining effort, then turns that information into a transparent daily planning view.

The program improves my study workflow in four ways. First, it keeps assessment information in one local file instead of spreading it across notes and browser tabs. Second, it gives each incomplete assessment a visible priority score so I can decide what deserves attention. Third, it records study sessions and produces a seven-day workload view. Fourth, it exports a simple CSV summary when I want to inspect the same information in a spreadsheet.

The project is intentionally a personal planning tool rather than a university system. It does not connect to Blackboard, scrape private data, or make academic decisions for me. The priority score is a heuristic that I can inspect and override.

## Main features

- Add assessments with unit code, title, due date, weight, estimated study hours and progress.
- List all assessments from highest to lowest planning priority.
- Update progress as work is completed.
- Log dated study sessions in minutes.
- Show a single "Today's Focus" recommendation.
- Show seven-day study and workload insights.
- Configure realistic daily study capacity.
- Export a non-sensitive assessment summary to CSV.
- Delete an assessment only after an explicit confirmation.
- Store data locally in JSON using only the Python standard library.

## How the priority score works

The score is deliberately simple and visible:

- **Urgency: 50%** - tasks closer to their due date receive a higher value.
- **Assessment weight: 25%** - higher-weight assessments receive more attention.
- **Remaining work: 25%** - lower progress means more work remains.

An overdue incomplete assessment receives a small capped boost. The final score is limited to 0-100. This is **not** a scientific model and is not intended to predict grades. It is a transparent planning heuristic, and the user remains responsible for deciding what to work on.

## Project structure

```text
02-project/
|-- main.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- assessmentflow/
|   |-- __init__.py
|   |-- core.py
|   |-- storage.py
|   `-- cli.py
|-- data/
|   `-- sample_data.json
`-- tests/
    `-- test_core.py
```

## Usage

### 1. Requirements

- Python 3.10 or newer is recommended.
- No `pip install` step is required.
- The program runs in a normal terminal, PowerShell, Command Prompt, macOS Terminal or Linux shell.

Check Python:

```bash
python --version
```

### 2. Start with your own local data

From inside the `02-project` folder:

```bash
python main.py
```

The default runtime data file is:

```text
data/assessmentflow.json
```

If the file does not exist, the program starts with an empty data set and creates the file when the user first saves information.

### 3. Run a safe demonstration with the supplied sample data

The included `data/sample_data.json` contains fictional demonstration information only. To view it without entering data manually:

```bash
python main.py --data data/sample_data.json --summary
```

For an interactive demonstration using a copy of the sample data, first copy the file and then run the copy. For example:

```bash
cp data/sample_data.json data/demo_working_copy.json
python main.py --data data/demo_working_copy.json
```

On Windows PowerShell, use:

```powershell
Copy-Item data\sample_data.json data\demo_working_copy.json
python main.py --data data\demo_working_copy.json
```

### 4. Optional custom data location

A different JSON file can be supplied with `--data`:

```bash
python main.py --data my_private_folder/my_assessments.json
```

The environment variable `ASSESSMENTFLOW_DATA` can also set the default path.

### 5. Run the automated tests

From inside `02-project`:

```bash
python -m unittest discover -s tests -v
```

## Data and privacy notes

The source-code ZIP includes only fictional sample data. Personal runtime data is excluded by `.gitignore` through `data/assessmentflow.json`, and the program does not transmit data over a network. If I use the program with real assessment information, I keep that personal data file outside the submitted ZIP and official repository.

## Error handling and reliability

The program validates numeric ranges and ISO dates before saving them. JSON saves use a temporary file followed by `os.replace`, reducing the chance that an interrupted write leaves a partially written data file. Invalid menu choices do not terminate the application. Deletion requires the user to type `DELETE`, which reduces accidental data loss.

## Open-source acknowledgements

AssessmentFlow does **not** import any third-party package and does not require `pip install`. It uses only Python 3 standard-library modules such as `argparse`, `csv`, `datetime`, `json`, `os` and `pathlib`. Therefore, there are no external software packages to list under this assignment requirement.

## Sociotechnical considerations

### 1. Privacy and data minimisation

**Design decision:** personal assessment data is stored locally in a user-selected JSON file, no account is required, there is no network transmission, and the submission includes fictional sample data rather than personal records. This decision treats privacy as an architectural concern rather than an afterthought. Recent software-engineering research similarly emphasises integrating privacy-enhancing decisions into the software development lifecycle (Klymenko et al., 2025).

The practical consequence is that the user has control over where the data is kept and can avoid putting sensitive information into GitHub or the Blackboard ZIP. The `.gitignore` file also excludes the default personal runtime file.

### 2. Human-centred transparency and user control

**Design decision:** AssessmentFlow shows the ingredients of its priority score instead of presenting an unexplained recommendation. The user can inspect due date, weight, progress, work remaining and the resulting score, then choose a different task if their real-life context requires it. The delete function also requires explicit confirmation. Human-centred software research highlights that users differ in their needs and that software design should account for those differences rather than forcing every user into the same interaction assumptions (Chauhan et al., 2024).

The program therefore supports a recommendation without treating the recommendation as an authority. This matters because a student may know about group commitments, extension arrangements or other circumstances that the program does not know.

### 3. Sustainability and maintainability

**Design decision:** the program uses the Python standard library only, keeps the codebase small and modular, and separates calculations, storage and user interaction. This reduces dependency maintenance and makes the program easier to run on an existing computer without additional installations. Contemporary software-engineering research treats sustainability as broader than energy use alone and includes product qualities such as evolvability and architecture (García-Mireles et al., 2026).

For this small personal tool, maintainability is the most relevant sustainability benefit: a future change to the priority formula can be made in `core.py` without rewriting the storage or interface code.

## Testing summary

Five automated unit tests are supplied in `tests/test_core.py`. They test remaining-hours calculation, priority ordering, focus selection, completed status and weekly metrics. In addition to these automated tests, the supplied sample data supports a repeatable manual demonstration of the complete command-line output.

## Limitations and future improvements

- The priority formula is a heuristic and does not account for task difficulty, dependencies or approved extensions unless the user updates the stored values.
- Progress is entered by the user rather than inferred from study-session minutes.
- The program is intentionally single-user and local; it does not synchronise across devices.
- A future version could add calendar import, configurable scoring weights and charts, provided those features do not compromise the privacy-first design.

## References

Chauhan, V., Arora, C., Khalajzadeh, H., & Grundy, J. (2024). How do software practitioners perceive human-centric defects? *Information and Software Technology, 176*, Article 107549. https://doi.org/10.1016/j.infsof.2024.107549

García-Mireles, G. A., Moraga, M. Á., García, F., & Calero, C. (2026). Sustainability in the field of software engineering: A tertiary study. *ACM Transactions on Software Engineering and Methodology, 35*(5), Article 141. https://doi.org/10.1145/3747178

Klymenko, A., Meisenbacher, S., Favaro, L., & Matthes, F. (2025). Supporting the integration of privacy-enhancing technologies into the software development life cycle. *SN Computer Science, 6*, Article 592. https://doi.org/10.1007/s42979-025-04127-6
