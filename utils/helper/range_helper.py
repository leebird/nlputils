class RangeHelper(object):
    @staticmethod
    def equal(range1, range2):
        return range1[0] == range2[0] and \
               range1[1] == range2[1]

    @staticmethod
    def overlap(range1, range2):
        return range1[1] >= range2[0] and \
               range1[0] <= range2[1]

    @staticmethod
    def char_range_overlap(entity1, entity2):
        return RangeHelper.overlap((entity1.char_start, entity1.char_end),
                                   (entity2.char_start, entity2.char_end))

    @staticmethod
    def token_range_overlap(entity1, entity2):
        return RangeHelper.overlap((entity1.token_start, entity1.token_end),
                                   (entity2.token_start, entity2.token_end))

    @staticmethod
    def include(outer_range, inner_range):
        return outer_range[0] <= inner_range[0] and \
               outer_range[1] >= inner_range[1]

    @staticmethod
    def char_range_include(outer_entity, inner_entity):
        return RangeHelper.include((outer_entity.char_start,
                                    outer_entity.char_end),
                                   (inner_entity.char_start,
                                    inner_entity.char_end))

    @staticmethod
    def token_range_include(outer_entity, inner_entity):
        return RangeHelper.include((outer_entity.token_start,
                                    outer_entity.token_end),
                                   (inner_entity.token_start,
                                    inner_entity.token_end))
