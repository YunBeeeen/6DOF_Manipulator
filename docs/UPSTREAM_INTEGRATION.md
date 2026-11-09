# 개인 저장소 통합 기준

원본 저장소: [lee-robot-lab/idle_ws](https://github.com/lee-robot-lab/idle_ws). 가져온 브랜치: `good_demo`, commit `22cb09910c3c946c037b8ecd10813a44433be459`.

개인 저장소의 이전 `main`은 `backup/pre-stage4-import-2026-11-09` 브랜치에 보존합니다. 기존 개인 코드 중 원본에 없는 파일도 유지합니다. 이번 가져오기는 출처를 기록한 소스 스냅샷이며, 원본 커밋 히스토리는 원본 저장소에서 확인합니다.

## 브랜치 선택

- `main`: 최신 `feature/stage4-integration` 기반. Stage1/2/4, ROS `demo_supervisor`, 기존 FSM/IK 제어, phase 정책 실험 코드.
- `upstream/good-demo-2026-07-01`: `good_demo` 기반. 카메라 1장·자연어→scene XML→MuJoCo/FSM 데모. [데모 절차](https://github.com/YunBeeeen/idle_ws/blob/upstream/good-demo-2026-07-01/docs/sim_natural_language_task_demo.md).

두 브랜치는 서로 갈라져 발전했으므로 일부 최신 파일만 섞어 하나의 검증된 실행본이라고 표시하지 않습니다. 전체 하드웨어 통합은 실행 환경에서 추가 확인이 필요합니다.

## 모델과 데이터

`UPSTREAM_ASSETS.json`은 `feature/stage4-integration` 고정 커밋의 원본 가중치·데이터 경로를 제공합니다. 기본 `--group weights`는 best checkpoint를 다운로드합니다. 학습 데이터는 manifest의 `dataset_url`에 기록된 원본 디렉토리에서 별도로 받을 수 있습니다. 로그·캐시·시각화 산출물과 재배포용 압축 파일은 새로 가져오지 않았습니다. 기존에 개인 저장소에 있던 자료는 유지합니다.

이 데모의 loader는 checkpoint 내부 `stage1_ckpt`, `color_net_ckpt` 경로를 따라갑니다. 원본 PC의 절대 경로가 저장돼 있을 수 있으므로, 해당 경로와 모델 구조가 현재 가중치와 맞는지 확인한 뒤 사용하세요. 최신 브랜치의 ColorNetV2를 이 브랜치에 그대로 끼워 넣지 마세요.

카메라·좌표계 calibration과 실제 모터 ID는 사용 환경에 맞춰 준비해야 합니다.

## 확인 범위

세 소스 스냅샷의 Python 파일 769개 문법 검사를 통과했습니다. 최신 통합 소스의 homography·데이터 분할 테스트 8개, 매핑 소스의 NumPy 정책·추정기 로그 테스트 3개를 직접 실행해 통과했습니다. PyTorch·ROS·MuJoCo가 없어 모델 추론과 전체 태스크는 실행하지 않았습니다.

파일별 출처·해시·제외 목록은 `UPSTREAM_IMPORT.json`을 참고하세요.
