# 실행 안내

모든 명령은 `idle_ws` 저장소 루트에서 실행합니다.

## Python 예제

```bash
python3 examples/relation_label_demo.py
```

Python 표준 라이브러리만 사용합니다. Stage4 학습 라벨의 기하 규칙을 확인하는 예제로, 학습된 신경망 추론과는 구분됩니다.

## ML 환경과 가중치

```bash
python3 -m pip install -r src/ml/requirements.txt
python3 download_upstream_assets.py --group weights --list
python3 download_upstream_assets.py --group weights
```

- `checkpoints/stage1_vitb14/best.pt`: Stage1 객체 슬롯 인코더
- `checkpoints/color_net_v2/best.pt`: ColorNetV2
- `checkpoints/stage4/best.pt`: Stage4 관계 모델

다운로드 파일의 크기·해시는 `UPSTREAM_ASSETS.json`에서 확인합니다. 학습 이미지는 해당 파일의 `dataset_url`에 연결된 원본 데이터 디렉토리에서 준비합니다.

## 카메라 이미지로 직접 지정 명령 처리

카메라가 연결되고 위 가중치가 준비된 환경에서 실행합니다. `--camera-device`는 현재 카메라의 인덱스에 맞춥니다. 이미지는 원본 1280×720 기준 crop·resize와 월드 좌표 calibration을 사용합니다.

```bash
PYTHONPATH="$PWD/src/ml${PYTHONPATH:+:$PYTHONPATH}" \
  python3 src/ml/stage4/vision_task_orchestrator.py \
  --text '파란 블록을 바구니에 넣어줘' \
  --parser rule --camera-device 0 --device cpu \
  --stage1-ckpt "$PWD/checkpoints/stage1_vitb14/best.pt" \
  --color-net-ckpt "$PWD/checkpoints/color_net_v2/best.pt" \
  --stage4-ckpt "$PWD/checkpoints/stage4/best.pt"
```

이 명령은 pick/place payload를 출력하며 ROS 명령을 발행하지 않습니다. 원본 실행 코드의 옵션은 `vision_task_orchestrator.py --help`에서 확인합니다. 신경망 학습·평가는 [ML README](../src/ml/README.md)를 참고하세요.

## ROS 2 워크스페이스

Ubuntu 22.04, ROS 2 Humble, C++17, Pinocchio, MuJoCo 및 `cv_bridge`를 사용합니다. 학습용 Python 환경과 ROS의 Python 환경에서 의존성이 동일하게 보이도록 준비합니다.

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
export PYTHONPATH="$PWD/src/ml${PYTHONPATH:+:$PYTHONPATH}"
```

실기 카메라는 `/image_raw`로 발행하고, 다른 토픽을 사용하면 `camera_topic`을 지정합니다. 모터 ID·CAN·그리퍼·제어 파라미터는 현재 로봇 구성에 맞춥니다.

```bash
ros2 launch demo_supervisor pick_place_demo.launch.py \
  stage1_ckpt:="$PWD/checkpoints/stage1_vitb14/best.pt" \
  color_net_ckpt:="$PWD/checkpoints/color_net_v2/best.pt" \
  stage4_ckpt:="$PWD/checkpoints/stage4/best.pt" \
  device:=cpu camera_topic:=/image_raw parser:=rule
```

CAN 브리지는 별도 터미널에서 `ros2 run can_interface can_bridge_node`로 실행합니다. 이 launch는 실제 제어 노드를 포함하므로 실기 연결·관절 설정을 완료한 환경에서 사용합니다. 작업 명령과 상태 인터페이스는 [ROS 데모 통합 안내](agent/ros_demo_integration_guide.md), 모터 제어는 [phy 문서](../src/phy/README.md)를 참고하세요.

## MuJoCo·별도 시뮬레이션 데모

- `src/sim/`: 로봇 모델·시뮬레이터
- `src/idle_launch/launch/sim_pickplace.launch.py`: 시뮬레이션 제어 launch. 원본의 `IDLE_PARAM_ROOT` 절대 경로를 현재 checkout의 `param/sim`에 맞춰 사용합니다.
- `upstream/good-demo-2026-07-01`: 자연어·카메라 장면을 MuJoCo XML로 변환하는 별도 데모. [실행 문서](https://github.com/YunBeeeen/idle_ws/blob/upstream/good-demo-2026-07-01/docs/sim_natural_language_task_demo.md).

실행 안내는 저장소의 현재 인자·파일 경로를 기준으로 작성했습니다. ROS·카메라·모터 실행은 해당 장치와 환경을 갖춘 시스템에서 확인해야 합니다.
