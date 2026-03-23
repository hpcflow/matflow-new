function generate_cubic_ODF_samples(inputs_JSON_path, outputs_HDF5_path)

    all_args = jsondecode(fileread(inputs_JSON_path));

    num_grains = all_args.num_grains;
    max_components = all_args.max_components;
    halfwidth_min = all_args.halfwidth_min;
    halfwidth_max = all_args.halfwidth_max;
    odf_fname = all_args.odf_fname;

    CS = crystalSymmetry('cubic');

    components = [...
    orientation.goss(CS),...
    orientation.brass(CS),...
    orientation.cube(CS),...
    orientation.cubeND22(CS),...
    orientation.cubeND45(CS),...
    orientation.cubeRD(CS),...
    orientation.copper(CS),...
    orientation.PLage(CS),...
    orientation.QLage(CS),...
    ];

    n_components = randi([1, max_components], 1);
    r = randperm(size(components, 2));
    r = r(1:n_components);
    halfwidth = rand(n_components,1) * (halfwidth_max - halfwidth_min) + halfwidth_min;
    weights = randfixedsum(n_components+1, 1, 1, 0, 1);

    for n = 1:n_components+1
        if n == 1
            odf_temp = uniformODF(CS);
            odf = weights(n) * SO3FunHarmonic(odf_temp, 'bandwidth', 16);
        else
            odf_temp = unimodalODF(components(r(n-1)), 'halfwidth', halfwidth(n-1)*degree);
            odf = odf + weights(n) * SO3FunHarmonic(odf_temp, 'bandwidth', 16);
        end
    end

    ori = odf.discreteSample(100000);
    odf = calcDensity(ori);
    odf = SO3FunHarmonic(odf, 'bandwidth', 16);
    orientations = odf.discreteSample(num_grains);
    export_orientations_HDF5(orientations, outputs_HDF5_path);

    save(odf_fname, 'odf');

end

function alignment = prepare_crystal_alignment(crystalSym)

    % as defined in MatFlow `LatticeDirection` enumeration class:
    keySet = {'a', 'b', 'c', 'a*', 'b*', 'c*'};
    valueSet = [0, 1, 2, 3, 4, 5];
    latticeDirs = containers.Map(keySet, valueSet);

    alignment = [];

    if isempty(crystalSym.alignment)
        % Cubic
        alignment(end + 1) = 0;
        alignment(end + 1) = 1;
        alignment(end + 1) = 2;
    else
        align1 = split(crystalSym.alignment{1}, '||');
        align2 = split(crystalSym.alignment{2}, '||');
        align3 = split(crystalSym.alignment{3}, '||');
        alignment(end + 1) = latticeDirs(align1{2});
        alignment(end + 1) = latticeDirs(align2{2});
        alignment(end + 1) = latticeDirs(align3{2});
    end

end

function export_orientations_HDF5(orientations, fileName)
    alignment = prepare_crystal_alignment(orientations.CS);
    ori_data = [orientations.a, orientations.b, orientations.c, orientations.d];

    % TODO: why?
    ori_data(:, 2:end) = ori_data(:, 2:end) * -1;

    ori_data = ori_data';
    h5create(fileName, '/orientations/data', size(ori_data));
    h5write(fileName, '/orientations/data', ori_data);
    h5writeatt(fileName, '/orientations', 'representation_type', 0);
    h5writeatt(fileName, '/orientations', 'representation_quat_order', 0);
    h5writeatt(fileName, '/orientations', 'unit_cell_alignment', alignment);
end

function [x,v] = randfixedsum(n,m,s,a,b)

    if (m~=round(m))|(n~=round(n))|(m<0)|(n<1)
        error('n must be a whole number and m a non-negative integer.')
    elseif (s<n*a)|(s>n*b)|(a>=b)
        error('Inequalities n*a <= s <= n*b and a < b must hold.')
    end

    s = (s-n*a)/(b-a);

    k = max(min(floor(s),n-1),0);
    s = max(min(s,k+1),k);
    s1 = s - [k:-1:k-n+1];
    s2 = [k+n:-1:k+1] - s;
    w = zeros(n,n+1); w(1,2) = realmax;
    t = zeros(n-1,n);
    tiny = 2^(-1074);
    for i = 2:n
        tmp1 = w(i-1,2:i+1).*s1(1:i)/i;
        tmp2 = w(i-1,1:i).*s2(n-i+1:n)/i;
        w(i,2:i+1) = tmp1 + tmp2;
        tmp3 = w(i,2:i+1) + tiny;
        tmp4 = (s2(n-i+1:n) > s1(1:i));
        t(i-1,1:i) = (tmp2./tmp3).*tmp4 + (1-tmp1./tmp3).*(~tmp4);
    end

    v = n^(3/2)*(w(n,k+2)/realmax)*(b-a)^(n-1);

    x = zeros(n,m);
    if m == 0, return, end
    rt = rand(n-1,m);
    rs = rand(n-1,m);
    s = repmat(s,1,m);
    j = repmat(k+1,1,m);
    sm = zeros(1,m); pr = ones(1,m);
    for i = n-1:-1:1
        e = (rt(n-i,:)<=t(i,j));
        sx = rs(n-i,:).^(1/i);
        sm = sm + (1-sx).*pr.*s/(i+1);
        pr = sx.*pr;
        x(n-i,:) = sm + pr.*e;
        s = s - e; j = j - e;
    end
    x(n,:) = sm + pr.*s;

    rp = rand(n,m);
    [ig,p] = sort(rp);
    x = (b-a)*x(p+repmat([0:n:n*(m-1)],n,1))+a;

end
