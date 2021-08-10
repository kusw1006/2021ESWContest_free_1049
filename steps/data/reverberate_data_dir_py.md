# From

> run_ivector_common.sh

# Param

> - rvb_opts 
>
> ```shell
> rvb_opts=()
> rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/smallroom/rir_list")
> rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/mediumroom/rir_list")
> rvb_opts+=(--noise-set-parameters RIRS_NOISES/pointsource_noises/noise_list)
> ```
>
> - -\-prefix "rev"
> - -\-foreground-snrs "20:10:15:5:0": iterate하며 해당 SNR로 노이즈 입혀짐
> - -\-background-snrs "20:10:15:5:0"
> - -\-speech-rvb-probability 1: rvb 적용 확률
> - -\-isotropic-noise-addition-probability 1: 적용할 확률
> - -\-num-replications ${num_data_reps = 1}: 노이즈 입힌 데이터 몇 종류 만들지 설정
> - -\-max-noises-per-minute 20
> - -\-source-sampling-rate 16000
> - -\-include-original-data true



# 코드분석

## main

```python
def main():
    args = get_args()

    # 목록 생성
    random.seed(args.random_seed)
    rir_list = parse_rir_list(args.rir_set_para_array, args.rir_smoothing_weight, args.source_sampling_rate)
    print("Number of RIRs is {0}".format(len(rir_list)))
    pointsource_noise_list = []
    iso_noise_dict = {}

    if args.noise_set_para_array is not None:
        pointsource_noise_list, iso_noise_dict = parse_noise_list(args.noise_set_para_array,
                                                                args.noise_smoothing_weight,
                                                                args.source_sampling_rate)
        print("Number of point-source noises is {0}".format(len(pointsource_noise_list)))
        print("Number of isotropic noises is {0}".format(sum(len(iso_noise_dict[key]) for key in iso_noise_dict.keys())))
    room_dict = make_room_dict(rir_list)

    if args.include_original_data == "true":
        include_original = True
    else:
        include_original = False
    
    # This function creates multiple copies of the necessary files, e.g. utt2spk, wav.scp ...
    create_reverberated_copy(input_dir = args.input_dir,
                           output_dir = args.output_dir,
                           room_dict = room_dict,
                           pointsource_noise_list = pointsource_noise_list,
                           iso_noise_dict = iso_noise_dict,
                           foreground_snr_string = args.foreground_snr_string,
                           background_snr_string = args.background_snr_string,
                           num_replicas = args.num_replicas,
                           include_original = include_original,
                           prefix = args.prefix,
                           speech_rvb_probability = args.speech_rvb_probability,
                           shift_output = args.shift_output,
                           isotropic_noise_addition_probability = args.isotropic_noise_addition_probability,
                           pointsource_noise_addition_probability = args.pointsource_noise_addition_probability,
                           max_noises_per_minute = args.max_noises_per_minute)


    data_lib.RunKaldiCommand("utils/validate_data_dir.sh --no-feats --no-text {output_dir}"
                    .format(output_dir = args.output_dir))

```



## (return) create_reverberated_copy

> This function creates multiple copies of the necessary files, e.g. utt2spk, wav.scp ...
>
> **/s5/data/train_clean_sp_rvb1/wav.scp에서 확인 가능**

```python
foreground_snr_array = [float(x) for x in foreground_snr_string.split(':')]
background_snr_array = [float(x) for x in background_snr_string.split(':')]

    
# reverb 여부를 무작위로 설정하고, 반향이 발생한 경우에 RIR를 샘플링함
# 또한 적절한 노이즈를 추가할지 여부를 결정
# 이 함수는 옵션 문자열을 binary wav-reverberate로 리턴
generate_reverberated_wav_scp(wav_scp, durations, output_dir, room_dict, \
                              pointsource_noise_list, iso_noise_dict, \
                              foreground_snr_array, background_snr_array, num_replicas,\
                              include_original, prefix,\
                              peech_rvb_probability, shift_output,\
                              isotropic_noise_addition_probability, \
                              pointsource_noise_addition_probability, max_noises_per_minute)

add_prefix_to_fields(input_dir + "/utt2spk", output_dir + "/utt2spk", num_replicas,\
                     include_original, prefix, field = [0,1])

data_lib.RunKaldiCommand("utils/utt2spk_to_spk2utt.pl <{output_dir}/utt2spk >\
						 {output_dir}/spk2utt".format(output_dir = output_dir))

if os.path.isfile(input_dir + "/utt2uniq"):
    add_prefix_to_fields(input_dir + "/utt2uniq", output_dir + "/utt2uniq", num_replicas, \
                         include_original, prefix, field =[0])
else:
	# Create the utt2uniq file
    create_corrupted_utt2uniq(input_dir, output_dir, num_replicas, include_original, prefix)

if os.path.isfile(input_dir + "/text"):
   	add_prefix_to_fields(input_dir + "/text", output_dir + "/text", num_replicas, \
                        include_original, prefix, field =[0])
if os.path.isfile(input_dir + "/segments"):
	add_prefix_to_fields(input_dir + "/segments", output_dir + "/segments", num_replicas,\
                         include_original, prefix, field = [0,1])
if os.path.isfile(input_dir + "/reco2file_and_channel"):
    add_prefix_to_fields(input_dir + "/reco2file_and_channel", output_dir + \
                         "/reco2file_and_channel", num_replicas, include_original, prefix, field\
                         = [0,1])
if os.path.isfile(input_dir + "/vad.scp"):
    add_prefix_to_fields(input_dir + "/vad.scp", output_dir + "/vad.scp", num_replicas, \
                         include_original, prefix, field=[0])

data_lib.RunKaldiCommand("utils/validate_data_dir.sh --no-feats --no-text {output_dir}" \
                         .format(output_dir = output_dir))
```



## generate_reverberated_wav_scp

> - 주요기능은 손상된 파이프라인 명령을 생성하는 것
>
> - wav-reverberate의 일반 명령은 다음과 같다
>
>   ```shell
>   wav-reverberate --duration=t --impulse-response=rir.wav
>           --additive-signals='noise1.wav,noise2.wav' --snrs='snr1,snr2' --start
>       	-times='s1,s2' input.wav output.wav
>   ```

```python
foreground_snrs = list_cyclic_iterator(foreground_snr_array)
background_snrs = list_cyclic_iterator(background_snr_array)
corrupted_wav_scp = {}
keys = sorted(wav_scp.keys())

if include_original:
    start_index = 0
else:
    start_index = 1

# num_replicas: 데이터에 대해 생성된 복제 수
for i in range(start_index, num_replicas+1):
    for recording_id in keys:
        wav_original_pipe = wav_scp[recording_id]
        # pipe가 없는 경우 뒤에 pipe 추가
        if len(wav_original_pipe.split()) == 1:
            wav_original_pipe = "cat {0} |".format(wav_original_pipe)
        speech_dur = durations[recording_id]
        
        # max_noises_per_minute: 1분 동안 녹음에 추가할 수 있는 point noise의 최대 수
        max_noises_recording = math.floor(max_noises_per_minute * speech_dur / 60)

        # 각종 노이즈 관련 옵션들을 리턴받음
        reverberate_opts = generate_reverberation_opts(room_dict,
                                                        pointsource_noise_list,
                                                        iso_noise_dict, 
                                                        foreground_snrs, 
                                                        background_snrs,
                                                        speech_rvb_probability,
                                                        isotropic_noise_addition_probability, 
                                                        pointsource_noise_addition_probability, 
                                                        speech_dur,  # duration of the recording
                                                        max_noises_recording 
                                                        )

        # 옵션들에 option붙여 pipe 생성
        # 전치사에 원본데이터의 몇번째 변형인지 숫자 붙이기
        # rvb0_swb0035 corresponds to the swb0035 recording in original data
        if reverberate_opts == "" or i == 0:
            wav_corrupted_pipe = "{0}".format(wav_original_pipe)
        else:
            wav_corrupted_pipe = "{0} wav-reverberate --shift-output={1} {2} - - |".format(wav_original_pipe, shift_output, reverberate_opts)

        # 변형된 데이터에 대한 scp 제작
        new_recording_id = get_new_id(recording_id, prefix, i)
        corrupted_wav_scp[new_recording_id] = wav_corrupted_pipe

# scp write
write_dict_to_file(corrupted_wav_scp, output_dir + "/wav.scp")
```



## generate_reverberation_opts

> - reverb 여부를 무작위로 설정하고, 반향이 발생한 경우에 RIR를 샘플링함
>
> - 또한 적절한 노이즈를 추가할지 여부를 결정
>
> - 이 함수는 옵션 문자열을 모아 reverberate_opts 문자열에 합침
>
>   (옵션 문자열 중 일부가 wav-reverberate …)

```python
# noise_addition_descriptor: descriptor to store the information of the noise added

reverberate_opts = ""
noise_addition_descriptor = {'noise_io': [],
                                'start_times': [],
                                'snrs': []}


# room 목록에서 하나 랜덤 픽
room = pick_item_with_probability(room_dict)
# 해당 룸의 RIR 중 하나 랜덤 픽
speech_rir = pick_item_with_probability(room.rir_list)

# 음성신호가 울릴확률 기준으로 낮을때
if random.random() < speech_rvb_probability:
    # RIR 불러서 옵션에 추가
    # rspecifier = read specifier <-> wspecifier
    reverberate_opts += """--impulse-response="{0}" """.format(speech_rir.rir_rspecifier)

# 룸 넘버가 iso_noise_dict에 있는 경우 iso_noise list에 추가
rir_iso_noise_list = []
if speech_rir.room_id in iso_noise_dict:
    rir_iso_noise_list = iso_noise_dict[speech_rir.room_id]

# isotropic noise 적용 확률보다 낮은 경우 iso noise 목록에있는 noise중 하나 랜덤 픽
if len(rir_iso_noise_list) > 0 and random.random() < isotropic_noise_addition_probability:
    isotropic_noise = pick_item_with_probability(rir_iso_noise_list)
    
    # iso noise를 음성 파형의 길이로 확장하는 정보를 descriptor에 저장
    # check if the rspecifier is a pipe or not
    if len(isotropic_noise.noise_rspecifier.split()) == 1:
        noise_addition_descriptor['noise_io'].append("wav-reverberate --duration={1} {0} -\
        |".format(isotropic_noise.noise_rspecifier, speech_dur))
    else:
        noise_addition_descriptor['noise_io'].append("{0} wav-reverberate --duration={1} - -\
        |".format(isotropic_noise.noise_rspecifier, speech_dur))
        
    noise_addition_descriptor['start_times'].append(0)
    noise_addition_descriptor['snrs'].append(next(background_snrs))


# add_point_source_noise: 위의 과정들과 마찬가지로 noise_addition_descriptor에 point noise 정보 추가  
noise_addition_descriptor = add_point_source_noise(noise_addition_descriptor,
                                                room,  # the room selected
                                                pointsource_noise_list,
                                                pointsource_noise_addition_probability,
                                                foreground_snrs,
                                                background_snrs,
                                                speech_dur, 
                                                max_noises_recording
                                                )

assert len(noise_addition_descriptor['noise_io']) == len(noise_addition_descriptor['start_times'])

assert len(noise_addition_descriptor['noise_io']) == len(noise_addition_descriptor['snrs'])

# descriptor의 noise_io에 있는 noise추가 정보 opts에 전달
if len(noise_addition_descriptor['noise_io']) > 0:
    reverberate_opts += "--additive-signals='{0}'\
    ".format(','.join(noise_addition_descriptor['noise_io']))
    
    reverberate_opts += "--start-times='{0}' ".format(','.join([str(x) for x in 
        noise_addition_descriptor['start_times']]))
    reverberate_opts += "--snrs='{0}' ".format(','.join([str(x) for x in 
        noise_addition_descriptor['snrs']]))

return reverberate_opts
```

